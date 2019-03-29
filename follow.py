import time
import sys
import io
import getpass
import logging
import requests

from instapy import InstaPy
from instapy import smart_run
from instapy.util import parse_cli_args

PRODUCTION = True

######################################
# configuration
#
# main customization
SLEEP_BETWEEN_EACH_FOLLOW = 25
SLEEP_BETWEEN_EACH_UNFOLLOW = 20
SLEEP_AFTER_ALL_FOLLOW = 240
HEADLESS_BROWSER = (True if PRODUCTION else False)
BYPASS_SUSPICIOUS_ATTEMPT = True
CHECK_IN_TO_SERVER = True
REPORT_STATUS_TO_SERVER = True
#
# default login credentials
DEFAULT_USERNAME = 'luchangzheng'
DEFAULT_PASSWORD = 'ilovebsb'
#
# other arguments for instapy
INT_MAX = sys.maxsize
SLEEP_DELAY = 25
UNFOLLOW_AFTER_AT_LEAST = 1
#
# server url to report
SERVER = ("http://socialgrow.live" if PRODUCTION else "http://localhost:3001")
CHECK_IN_URL = SERVER + "/admin/check-in"
REPORT_STATUS_URL = SERVER + "/admin/report-status"
#######################################


# instagram follow targets data
users_celebrity = ['justinbieber', 'taylorswift', 'selenagomez', 'kimkardashian', 'arianagrande', 'instagram',
                   'beyonce', 'kyliejennr', 'katyperry', 'therock']
users_test_subset = ['justinbieber', 'taylorswift']
users_test_single = ['justinbieber']
users = users_celebrity

# backup stdout and stderr
stdout = sys.stdout
stderr = sys.stderr
# set a global logger
logger = logging.getLogger()


# the main function
def main():
    # build up communication with instapy. Hack print() and logger
    # (1) redirect stdout/stderr to customised string streams
    # (2) for each instapy IO operation, report it's buffer to node.js server
    #
    class MyIO(io.StringIO):
        def __init__(self):
            super(MyIO, self).__init__()
            self.report = False
            self.reporter = None

        def begin_report(self, yes_or_no):
            self.report = yes_or_no

        def set_reporter(self, r):
            self.reporter = r

        def write(self, buffer):
            super(MyIO, self).write(buffer)
            stdout.write(buffer)
            if self.report and self.reporter is not None:
                self.reporter.send(buffer)

    class Reporter:
        def __init__(self, ig_user, sys_user):
            self.ig_user = ig_user
            self.sys_user = sys_user

        def send(self, buffer):
            # call report_status function
            report_status(self.ig_user, self.sys_user, buffer)

    # redirect streams
    stream = MyIO()
    sys.stderr = stream
    sys.stdout = MyIO()  # another stream for stdout, do not enable report on this stream
    # sys.stdout = io.StringIO()  # or discard everything in stdout by directing to a never-use stream

    # check in this process to server
    cli_args = parse_cli_args()
    instagram_user = cli_args.username or DEFAULT_USERNAME
    system_user = getpass.getuser()
    if CHECK_IN_TO_SERVER:
        check_in(instagram_user, system_user)

    # setup reporter for stderr stream
    reporter = Reporter(instagram_user, system_user)
    stream.set_reporter(reporter)
    if REPORT_STATUS_TO_SERVER:
        stream.begin_report(True)

    # get an InstaPy session!
    # set headless_browserTrue to run InstaPy in the background
    session = InstaPy(username=DEFAULT_USERNAME,
                      password=DEFAULT_PASSWORD,
                      headless_browser=HEADLESS_BROWSER,
                      bypass_suspicious_attempt=BYPASS_SUSPICIOUS_ATTEMPT)

    # run the task
    with smart_run(session):

        # activities
        while True:

            # follow users
            for user in users:
                session.follow_by_list([user],
                                       times=INT_MAX,
                                       sleep_delay=SLEEP_DELAY,
                                       interact=False)
                time.sleep(SLEEP_BETWEEN_EACH_FOLLOW)

            # lunch break
            logger.warning("[sleep {0} seconds before unfollowing]".format(SLEEP_AFTER_ALL_FOLLOW))
            time.sleep(SLEEP_AFTER_ALL_FOLLOW)

            # unfollow users
            for user in users:
                session.unfollow_users(customList=(True, [user], "all"),
                                       style="RANDOM",
                                       unfollow_after=UNFOLLOW_AFTER_AT_LEAST,
                                       sleep_delay=SLEEP_DELAY)
                time.sleep(SLEEP_BETWEEN_EACH_UNFOLLOW)


# check in to server
def check_in(instagram_user, system_user):
    # print("\n[check in]")
    data = {'instagramUser': instagram_user,
            'systemUser': system_user}
    try:
        requests.post(url=CHECK_IN_URL, data=data)
    except ConnectionError:
        pass


# report status to server
def report_status(instagram_user, system_user, buffer):
    # print("[report status]\n")
    buffer = buffer.rstrip()
    if buffer == "":
        return

    data = {'instagramUser': instagram_user,
            'systemUser': system_user,
            'message': buffer}
    try:
        requests.post(url=REPORT_STATUS_URL, data=data)
    except ConnectionError:
        pass

# call main function
main()
