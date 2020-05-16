import time
import pandas as pd
import requests
from requests_oauthlib import OAuth1
from accessPoints_Sprejer import TwitterAuth51 as auth


seed_users = list(pd.read_csv("data/seed_users.csv").user_id.values)
retweeters_users = list(pd.read_csv("data/retweeters_users.csv").user_id.values)

oauth = OAuth1(auth.consumer_key,
               auth.consumer_secret,
               auth.access_token,
               auth.access_token_secret)


def get_followers(user_id_list, n_seeds):
    times = [] # Control not exceeding the rate limit
    
    for idx, user_id in enumerate(user_id_list):
        user_type = "seed" if idx < n_seeds else "retweeters"
        cursor = -1 # Controls pagination
        
        while cursor != 0: # When cursor == 0 means end of pagination
            if len(times) == 15: # if 15 requests were already done
                if times[-1] - times[0] < 900: # check not exceding the rate limit
                    print("waiting the needed time before continuing")
                    time.sleep(901-(times[-1] - times[0])) # wait the rest of the 15 minutes
                times = times[1:] # remove the initial time 
                        
            times.append(time.time()) # adding time of the new request
            
            url = "https://api.twitter.com/1.1/followers/ids.json?" + \
            "user_id={}".format(user_id) + "&count=5000" + "&cursor={}".format(cursor)
            response = requests.get(url,
                                    auth=oauth)
            try:
                with open('data/processed/{}_followers/{}_followers_{}.csv'.format(user_type, user_type, time.strftime("%y%m%d")), 'a') as f: 
                    for follower_id in response.json()['ids']:
                        f.write(str(user_id) + "," + str(follower_id) + "\n")
            except:
                print(user_id, response.json())
            cursor = response.json()['next_cursor']
            
if __name__ == "__main__":
    get_followers(seed_users + retweeters_users, n_seeds = len(seed_users))
    

    