
# Simple update script for Linux

echo "Updating InstaPy..."
echo "===================="
pip install -U instapy

apt-get install firefox
git clone https://github.com/1665673/InstaGrow.git
cd InstaGrow
cp firefox/geckodriver.ubuntu /usr/local/bin/geckodriver
pip3 install -r requirements.txt
