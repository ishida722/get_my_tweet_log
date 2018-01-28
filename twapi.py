import secret
import twitter
import sys
from datetime import datetime, timezone, timedelta, date
from EsDataConverter.EsDataConverter import Converter
from elasticsearch import Elasticsearch
import os

SCREEN_NAME = 'paragraph_14'
COUNT = 200
JST = timezone(timedelta(hours=+9), 'Tokyo')

class API:
    api = twitter.Api(
            consumer_key=secret.TWITTER_CONSUMER_KEY,
            consumer_secret=secret.TWITTER_CONSUMER_SECRET,
            access_token_key=secret.TWITTER_ACCESS_TOKEN,
            access_token_secret=secret.TWITTER_ACCESS_TOKEN_SECRET
            )

def GetDateTime(time):
    time = datetime.strptime(time, '%a %b %d %H:%M:%S %z %Y')
    time = time.astimezone(JST)
    return time

def GetDateTimeStr(time):
    time = GetDateTime(time)
    return time.strftime('%Y-%m-%dT%H:%M:%SZ')

def HowManyDaysAgo(tweet):
    today = datetime.now(JST).date()
    time = GetDateTime(tweet.created_at).date()
    return (today - time).days

def GetDateStr(created_at_in_seconds):
    date = datetime.fromtimestamp(created_at_in_seconds, JST)
    dateStr = date.strftime('%Y%m%dT%H%M%SZ')
    return dateStr

def GetYesterdayTweets():
    tw = API()
    retTweets = []
    nowEndId = None
    isTweetTodayOrYesterday = True
    while isTweetTodayOrYesterday:
        rawResult = tw.api.GetUserTimeline(screen_name=SCREEN_NAME, count=COUNT, max_id=nowEndId)
        for tweet in rawResult:
            days = HowManyDaysAgo(tweet)
            nowEndId = tweet.id
            if days == 1: #Yesteday
                retTweets.append({'usr':tweet.user.screen_name, 'date':GetDateStr(tweet.created_at_in_seconds), 'text':tweet.text})
            elif days > 1:
                isTweetTodayOrYesterday = False
                break
    return retTweets

if __name__ == '__main__':
    tweets = GetYesterdayTweets()
    es  = Elasticsearch(os.getenv('ES_SERVER', 'http://localhost:9200'))
    for tweet in tweets:
        res = es.index(index='twitter', doc_type='my_timeline', body=tweet)
        print(res)
