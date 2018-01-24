import secret
import twitter
import sys
from datetime import datetime, timezone, timedelta, date

SCREEN_NAME = 'paragraph_14'
COUNT = 200

class API:
    api = twitter.Api(
            consumer_key=secret.TWITTER_CONSUMER_KEY,
            consumer_secret=secret.TWITTER_CONSUMER_SECRET,
            access_token_key=secret.TWITTER_ACCESS_TOKEN,
            access_token_secret=secret.TWITTER_ACCESS_TOKEN_SECRET
            )


def GetDateTime(time):
    time = datetime.strptime(time, '%a %b %d %H:%M:%S %z %Y')
    time = time.astimezone(timezone(timedelta(hours=+9), 'Tokyo'))
    return time

def GetDateTimeStr(time):
    time = GetDateTime(time)
    return time.strftime('%Y-%m-%dT%H:%M:%SZ')

def IsItToday(tweet):
    today = datetime.now(timezone(timedelta(hours=+9), 'Tokyo')).date()
    time = GetDateTime(tweet.created_at).date()
    if (today - time).days < 1:
        return True
    return False

def IsItYesterday(tweet):
    today = datetime.now(timezone(timedelta(hours=+9), 'Tokyo')).date()
    time = GetDateTime(tweet.created_at).date()
    if (today - time).days == 1:
        return True
    return False

def HowManyDaysAgo(tweet):
    today = datetime.now(timezone(timedelta(hours=+9), 'Tokyo')).date()
    time = GetDateTime(tweet.created_at).date()
    return (today - time).days

def GetYesterdayTweets():
    tw = API()
    retTweets = []
    nowCount = 0
    nowEndId = None
    rawResult = tw.api.GetUserTimeline(screen_name=SCREEN_NAME, count=COUNT, max_id=nowEndId)
    for tweet in rawResult:
        days = HowManyDaysAgo(tweet)
        if days == 1:
            retTweets.append(tweet)
        elif days > 1:
            break
    return retTweets

def main():
    tw = API()
    nowCount = 0
    nowEndId = None
    with open('tweets.csv', 'w') as f:
        f.write('timestamp, tweet\n')
        while True:
            rawResult = tw.api.GetUserTimeline(screen_name=SCREEN_NAME, count=COUNT, max_id=nowEndId)
            if not rawResult: sys.exit()
            nowCount = nowCount + COUNT
            for status in rawResult:
                if not IsItToday(status): sys.exit()
                time = GetDateTimeStr(status.created_at)
                txt = status.text.replace('\n', '')
                f.write('{}, "{}"\n'.format(time, txt))
            print(nowCount)
            nowEndId = rawResult[-1].id - 1

if __name__ == '__main__':
    print(GetYesterdayTweets())
