import tweepy
import pandas as pd
import json
import time
from accessPoints_nate import TwitterAuth50 as auth

seed_users = pd.read_csv("data/seed_users.csv")
ids = list(seed_users.user_id.astype(str).values)
users = list(seed_users.screen_name.values)

dict_users = {}
for idx, user_id in enumerate(ids):
    dict_users[user_id] = users[idx]

oauth = tweepy.OAuthHandler(auth.consumer_key, auth.consumer_secret)
oauth.set_access_token(auth.access_token, auth.access_token_secret)
api = tweepy.API(oauth)

class screen_name_error(Exception):
    """Raise error if screen_name changed"""
    def __init__(self, user_id, screen_name):
        self.user_id = user_id
        self.screen_name = screen_name

class StreamListener(tweepy.StreamListener):
    def __init__(self, dict_users=dict_users):
        super(StreamListener,self).__init__()
        
    def on_status(self, status):

        # Write the json data directly to the file
        with open('data/raw/seed_tweets/stream_tweets_{}.json'.format(time.strftime("%y%m%d")), 'a') as tf:
            json.dump(status._json, tf)
            tf.write('\n')
        
        #print(status.text)
        
        ### Check if screen name changed ###        
        if tweet["user"]['id_str'] in dict_users: # Check if it is a seed tweet
            if tweet["user"]['screen_name'] != dict_users[tweet["user"]['id_str']]: # Check if the screen_name changed
                raise screen_name_error(tweet["user"]['id'], tweet["user"]['screen_name'])
            
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
        
        except screen_name_error as screen_name_change:
            print("Screen name changed", screen_name_change.user_id, screen_name_change.screen_name)

            # Modify seed file
            seed_users.loc[seed_users.user_id == screen_name_change.user_id, 'screen_name'] = screen_name_change.screen_name
            seed_users.to_csv("data/seed_users.csv", index=False)
            
            # Modify screen_names list
            users = list(seed_users.screen_name.astype(str).values)
            
        except Exception:
            print("error. Restarting Stream... Error:")
            time.sleep(60)



