import secret
import twitter
import sys
from datetime import datetime, timezone, timedelta, date
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

def HowManyDaysAgo(tweet):
    today = datetime.now(JST).date()
    created = datetime.fromtimestamp(tweet.created_at_in_seconds, JST).date()
    return (today - created).days

def GetDateStr(created_at_in_seconds):
    date = datetime.fromtimestamp(created_at_in_seconds, JST)
    dateStr = date.strftime('%Y-%m-%dT%H:%M:%S+09:00')
    return dateStr

YESTERDAY = 1
TODAY = 0

def GetTweets(day):
    tw = API()
    retTweets = []
    nowEndId = None
    isTweetTodayOrYesterday = True
    while isTweetTodayOrYesterday:
        rawResult = tw.api.GetUserTimeline(screen_name=SCREEN_NAME, count=COUNT, max_id=nowEndId)
        for tweet in rawResult:
            days = HowManyDaysAgo(tweet)
            nowEndId = tweet.id
            if days == day or tweet.retweeted == True : #Yesteday
                retTweets.append({'user':tweet.user.screen_name, 'date':GetDateStr(tweet.created_at_in_seconds), 'text':tweet.text})
            elif days > day:
                isTweetTodayOrYesterday = False
                break
    return retTweets

def IndexTweets(day):
    tweets = GetTweets(day)
    es  = Elasticsearch(os.getenv('ES_SERVER', 'http://localhost:9200'))
    for tweet in tweets:
        res = es.index(index='twitter', doc_type='tweet', body=tweet)
        print(res)
    return res

def PrintTweet(day):
    tweets = GetTweets(day)
    for tw in tweets:
        print('{} : {} : {}'.format(tw['user'], tw['text'], tw['date']))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Get tweetlog')
    parser.add_argument('-p', '--print', action='store_true',  help='print only')
    parser.add_argument('-d', '--day', default=YESTERDAY,  help='day')
    args = parser.parse_args()

    day = YESTERDAY
    print(args.day)

    if args.print: # -p --print option
        PrintTweet(day)
    else:
        IndexTweets(day)
