import tweepy
import pandas as pd
import sys
import json
import time
from accessPoints_Sprejer import TwitterAuth50 as auth

ids = list(pd.read_csv("seed_users.csv",converters={'id': str}).id.values)
users = list(pd.read_csv("seed_users.csv").user.values)
    
oauth = tweepy.OAuthHandler(auth.consumer_key, auth.consumer_secret)
oauth.set_access_token(auth.access_token, auth.access_token_secret)
api = tweepy.API(oauth)

class StreamListener(tweepy.StreamListener):
    def __init__(self, output_file=sys.stdout):
        super(StreamListener,self).__init__()
        
    def on_status(self, status):
        with open('data/seed_tweets/seed_tweets_{}.json'.format(time.strftime("%y%m%d")), 'a') as tf:
            
            # Write the json data directly to the file
            json.dump(status._json, tf)
            
            tf.write('\n')
        
        print(status.text)

    def on_error(self, status_code):
        if status_code == 420:
            return False


if __name__ == "__main__":
    while True:
        stream_listener = StreamListener()
        stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
        try:
            print("streaming...")
            stream.filter(follow=ids, track=users)
        except Exception:
            print("error. Restarting Stream... Error:")
            time.sleep(60)



