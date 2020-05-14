import time
import pandas as pd
import requests
from requests_oauthlib import OAuth1
from accessPoints_Sprejer import TwitterAuth53 as auth


seed_users = list(pd.read_csv("data/seed_users.csv").user_id.values)
retweeters_users = list(pd.read_csv("data/retweeters_users.csv").user_id.values)

oauth = OAuth1(auth.consumer_key,
               auth.consumer_secret,
               auth.access_token,
               auth.access_token_secret)


def get_friends(user_id_list, n_seeds):
    times = [] # Control not exceeding the rate limit
    
    for idx, user_id in enumerate(user_id_list):
        user_type = "seed" if idx < n_seeds else "retweeters"
        print(user_id)
        cursor = -1 # Controls pagination
        
        while cursor != 0: # When cursos == 0 means end of pagination
            print(cursor)
            if len(times) == 15: # if 15 requests were already done
                if times[-1] - times[0] < 900: # check not exceding the rate limit
                    print("waiting the needed time before continuing")
                    time.sleep(900-(times[-1] - times[0])) # wait the rest of the 15 minutes
                times = times[1:] # remove the initial time 
                        
            times.append(time.time()) # adding time of the new request
            url = "https://api.twitter.com/1.1/friends/ids.json?" + \
            "user_id={}".format(user_id) + "&count=5000" + "&cursor={}".format(cursor)
            response = requests.get(url,
                                    auth=oauth)

            with open('data/processed/{}_friends/friends_{}_{}.csv'.format(user_type,user_id,time.strftime("%y%m%d")), 'a') as f: 
                for friend_id in response.json()['ids']:
                    f.write("%s\n" % friend_id)
                        
            cursor = response.json()['next_cursor']
            
if __name__ == "__main__":
    get_friends(seed_users + retweeters_users, len(seed_users))

    

    