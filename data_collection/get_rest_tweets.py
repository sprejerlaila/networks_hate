import time
import datetime as dt
import pandas as pd
import requests
from accessPoints_nate import TwitterAuth84 as auth
from requests_oauthlib import OAuth1
import json

oauth = OAuth1(auth.consumer_key,
               auth.consumer_secret,
               auth.access_token,
               auth.access_token_secret)

class get_tweets():
    
    def __init__(self, users_df, since, until, file_path):
        self.since = time.strptime(since, '%Y-%m-%d')
        self.until = until
        
        users = users_df
        users['screen_name'] = '@' + users['screen_name'].astype(str)

        # print('getting timeline')
        # self.get_timeline(users['user_id'].values, file_path)
        
        print('getting mentions')
        self.get_mentions(users['screen_name'].values, file_path)

        
    def get_timeline(self, users, file_path):
        until = time.strptime(self.until, '%Y-%m-%d')
        times = [] # Control rate limit.       

        for user_id in users:
            print("User id: ", user_id, end=" - ")
            count = 0
            max_id = None
            while True:

                if len(times) == 900: # if 900 requests were already done
                    if times[-1] - times[0] < 900: # check not exceding the rate limit (15 min window)
                        print("waiting the needed time before continuing")
                        time.sleep(901-(times[-1] - times[0])) # wait the rest of the 15 minutes
                    times = times[1:] # remove the initial time 
                times.append(time.time()) # adding time of the new request

                response = requests.get("https://api.twitter.com/1.1/statuses/user_timeline.json",
                                params = {"user_id": user_id, "tweet_mode": "extended", "count":200, "max_id":max_id},
                                auth=oauth)
                response = response.json()

                for tweet in response:
                    try:
                        tw_date = time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
                    except:
                        print(response)
                        break
                    
                    if tw_date > self.since and tw_date < until:
                        # Write the json data directly to the file
                        with open(file_path + 'rest_tweets_{}.json'.format(time.strftime("%y%m%d", self.since)), 'a') as tf:
                            json.dump(tweet, tf)
                            tf.write('\n')
                        count +=1
                
                if tw_date < self.since: # tw_date is the date of the last tweet collected
                    break
                else:
                    max_id = tweet['id']
            print("n timeline tweets: ", count)

    def get_mentions(self, users, file_path):
        times = []
        count = 0 
        for screen_name in users:
            print("screen_name: ", screen_name, end=" - ")
            next_page_url = "https://api.twitter.com/1.1/search/tweets.json?until={}".format(self.until)
            count = 0 
            while True:
                if len(times) == 180: # if 180 requests were already done
                    if times[-1] - times[0] < 900: # check not exceding the rate limit (15 min window)
                        print("waiting the needed time before continuing")
                        time.sleep(901-(times[-1] - times[0])) # wait the rest of the 15 minutes
                    times = times[1:] # remove the initial time 
                            
                times.append(time.time()) # adding time of the new request
                
                response = requests.get(next_page_url,
                                    params = {"q": screen_name, "count":200,  "tweet_mode": "extended"},
                                    auth=oauth)
    
                response = response.json()

                if 'statuses' not in response:
                    print(response)
                    break

                for tweet in response['statuses']:
                    tw_date = time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
                    if tw_date > self.since:
                        # Write the json data directly to the file
                        with open(file_path + 'rest_tweets_{}.json'.format(time.strftime("%y%m%d",self.since)), 'a') as tf:
                            json.dump(tweet, tf)
                            tf.write('\n')
                        count +=1
                
                    if tw_date < self.since:
                        break
                if 'next_results' in response['search_metadata']:
                    next_page_url = "https://api.twitter.com/1.1/search/tweets.json" \
                    + response['search_metadata']['next_results']
                else:
                    break
            print("n mentions: ", count)
            #print(response) ### Once the collection breaks, check the last response

if __name__ == "__main__":
    users_df = pd.read_csv("data/seed_users.csv")
    yesterday = dt.datetime.strftime(dt.datetime.now() - dt.timedelta(1), '%Y-%m-%d')
    today = time.strftime("%Y-%m-%d")
    print("Collecting tweets from {} to {}".format(yesterday, today))
    get_tweets(users_df = users_df, since=yesterday, until=today, file_path = 'delete/')#'data/raw/seed_tweets/')
    
