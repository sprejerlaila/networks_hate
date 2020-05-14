import time
import datetime as dt
import pandas as pd
import requests
from accessPoints_Sprejer import TwitterAuth52 as auth
from requests_oauthlib import OAuth1
import json


oauth = OAuth1(auth.consumer_key,
               auth.consumer_secret,
               auth.access_token,
               auth.access_token_secret)



class get_tweets():
    
    def __init__(self, since, until):
        self.since = time.strptime(since, '%Y-%m-%d')
        self.until = until
        
        users = pd.read_csv("data/seed_users.csv")
        users['screen_name'] = '@' + users['screen_name'].astype(str)
        
        for idx, row in users.iterrows():
            self.get_timeline(row['user_id'])
            self.get_mentions(row['screen_name'])
        

        
    def get_timeline(self, user_id):
        #TODO add pagination!!! 
        until = time.strptime(self.until, '%Y-%m-%d')
        response = requests.get("https://api.twitter.com/1.1/statuses/user_timeline.json",
                        params = {"user_id": user_id, "tweet_mode": "extended"},
                        auth=oauth)
        
        for tweet in response.json():
            tw_date = time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
            if tw_date > self.since and tw_date < until:
                with open('data/raw/seed_tweets/rest_tweets_{}.json'.format(time.strftime("%y%m%d", self.since)), 'a') as tf:
                
                    # Write the json data directly to the file
                    json.dump(tweet, tf)
                    
                    tf.write('\n')

    def get_mentions(self, screen_name):
        next_page_url = "https://api.twitter.com/1.1/search/tweets.json"
        while True:
            response = requests.get(next_page_url,
                                params = {"q": screen_name, "count":200, "until":self.until, "tweet_mode": "extended"},
                                auth=oauth)

            response = response.json()
            
            for tweet in response['statuses']:
                tw_date = time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
                if tw_date > self.since:
                    with open('data/raw/seed_tweets/rest_tweets_{}.json'.format(time.strftime("%y%m%d",self.since)), 'a') as tf:
                    
                        # Write the json data directly to the file
                        json.dump(tweet, tf)
                        
                        tf.write('\n')
            
            if tw_date < self.since:
                break    
            next_page_url = "https://api.twitter.com/1.1/search/tweets.json" \
            + response['search_metadata']['next_results']

if __name__ == "__main__":
    yesterday = dt.datetime.strftime(dt.datetime.now() - dt.timedelta(1), '%Y-%m-%d')
    today = time.strftime("%Y-%m-%d")
    get_tweets(since=yesterday, until=today)