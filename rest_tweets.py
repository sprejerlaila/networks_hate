import time
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
        
        users = list(pd.read_csv("seed_users.csv").user.values)
        users = ["@"+user for user in users]
        for user in users:
            self.get_timeline(user)
            self.get_mentions(user)
        

        
    def get_timeline(self, user):
        #TODO add pagination!!! 
        until = time.strptime(self.until, '%Y-%m-%d')
        response = requests.get("https://api.twitter.com/1.1/statuses/user_timeline.json",
                        params = {"screen_name": user, "tweet_mode": "extended"},
                        auth=oauth)
        
        for tweet in response.json():
            tw_date = time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
            if tw_date > self.since and tw_date < until:
                with open('data/seed_tweets/rest_tweets_{}.json'.format(time.strftime("%y%m%d", self.since)), 'a') as tf:
                
                    # Write the json data directly to the file
                    json.dump(tweet, tf)
                    
                    tf.write('\n')

    def get_mentions(self, user):
        next_page_url = "https://api.twitter.com/1.1/search/tweets.json"
        while True:
            response = requests.get(next_page_url,
                                params = {"q": user, "count":200, "until":self.until, "tweet_mode": "extended"},
                                auth=oauth)

            response = response.json()
            
            for tweet in response['statuses']:
                tw_date = time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
                if tw_date > self.since:
                    with open('data/seed_tweets/rest_tweets_{}.json'.format(time.strftime("%y%m%d",self.since)), 'a') as tf:
                    
                        # Write the json data directly to the file
                        json.dump(tweet, tf)
                        
                        tf.write('\n')
            
            if tw_date < self.since:
                break    
            next_page_url = "https://api.twitter.com/1.1/search/tweets.json" \
            + response['search_metadata']['next_results']
