import datetime
import time
import argparse
import requests
import sys
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument("username", help="Username or email to log in")
parser.add_argument("password", help="Password for account")
parser.add_argument("--timestamp", type=int, default=time.time() - 86400, help="Timestamp of last scraping")
parser.add_argument("-v", "--verbosity", action="store_true", help="increase output verbosity")
args = parser.parse_args()

def log(msg):
    if args.verbosity:
        print(msg)

log('username: ' + args.username)
log('password: ' + args.password)
log('timestamp: ' + str(args.timestamp))

url = 'https://slashdot.org/my/login'
payload = {
    'unickname': args.username,
    'upasswd': args.password
}

session = requests.Session()
res = session.post(url, data=payload)

soup = BeautifulSoup(res.text)
#print(soup.get_text().encode('UTF-8'))
#print(soup.prettify().encode('UTF-8'))

if res.status_code != 200 or soup.find(href='//slashdot.org/my/login'):
    print("Login failed")
    sys.exit()
else:
    log('Login: ' + str(res.status_code))

dateCutOff = datetime.datetime.fromtimestamp(args.timestamp)

page = 0
scrapePage = True
data = []
while scrapePage:
    articles = soup.find(id='firehoselist').find_all('article')

    log(str(len(articles)) + ' articles on page ' + str(page))

    for article in articles:
        story = article.find(class_='story').find('a').get_text().encode('UTF-8')
        author = article.find(class_='details').find('a').get_text().encode('UTF-8')
        dateArticle = article.find(class_='details').find('time').get_text()
        dateArticle = datetime.datetime.strptime(dateArticle, 'on %A %B %d, %Y @%I:%M%p')
        if dateArticle > dateCutOff:
            log('story: ' + dateArticle.isoformat() + ' [' + author + '] ' + story)
            data.append({
                'headline': story,
                'author': author,
                'date': time.mktime(dateArticle.timetuple())
            })
        else:
            scrapePage = False

    page += 1
    if scrapePage:
        res = session.get('https://slashdot.org/?page=' + str(page))
        soup = BeautifulSoup(res.text)

log('Done')
print(data)