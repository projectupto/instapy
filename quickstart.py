

# imports
from instapy import InstaPy
from instapy.util import smart_run
import time
import sys

# login credentials
insta_username = 'prestonwucong'
insta_password = 'anquandemima99'
INT_MAX = sys.maxsize


users_celebrity = ['justinbieber','taylorswift','selenagomez','kimkardashian','arianagrande','instagram','beyonce','kyliejenner','katyperry','therock']
users_test_subset = ['justinbieber','taylorswift']
users_test_single = ['justinbieber']

users = users_celebrity

# get an InstaPy session!
# set headless_browserTrue to run InstaPy in the background
session = InstaPy(username=insta_username,
                  password=insta_password,
                  headless_browser=False)

with smart_run(session):
    """ Activity flow """
    while True:
        for user in users:
            session.follow_by_list([user], times=INT_MAX,sleep_delay=0, interact=False)
            time.sleep(10)

        time.sleep(100)
        
        for user in users:
            session.unfollow_users(customList=(True, [user], "all"), style="RANDOM", unfollow_after=100, sleep_delay=0)
            time.sleep(10)


        
