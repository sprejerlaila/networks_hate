import sys
import math
import time
import pandas as pd
import requests
from requests_oauthlib import OAuth1
from accessPoints_Sprejer import TwitterAuth53 as auth_seed
from accessPoints_Sprejer import TwitterAuth44 as auth0
from accessPoints_Sprejer import TwitterAuth45 as auth1

seed_users = list(pd.read_csv("data/seed_users.csv").user_id.values)
retweeters_users = list(pd.read_csv("data/retweeters_users.csv").user_id.values)


oauth_seed = OAuth1(auth_seed.consumer_key, auth_seed.consumer_secret, auth_seed.access_token, auth_seed.access_token_secret)

oauth0 = OAuth1(auth0.consumer_key, auth0.consumer_secret, auth0.access_token, auth0.access_token_secret)

oauth1 = OAuth1(auth1.consumer_key, auth1.consumer_secret, auth1.access_token, auth1.access_token_secret)

oauths = [oauth0, oauth1]


def get_friends(user_id_list, n_seeds, oauth=oauth0, n_group = 0, datetime=time.strftime("%y%m%d")):
    times = [] # Control not exceeding the rate limit
    
    for idx, user_id in enumerate(user_id_list):
        user_type = "seed" if idx < n_seeds else "retweeters"
        cursor = -1 # Controls pagination
        
        while cursor != 0: # When cursos == 0 means end of pagination
            if len(times) == 15: # if 15 requests were already done
                if times[-1] - times[0] < 900: # check not exceding the rate limit
                    print("waiting the needed time before continuing")
                    time.sleep(901-(times[-1] - times[0])) # wait the rest of the 15 minutes
                times = times[1:] # remove the initial time 
                        
            times.append(time.time()) # adding time of the new request
            url = "https://api.twitter.com/1.1/friends/ids.json?" + \
            "user_id={}".format(user_id) + "&count=5000" + "&cursor={}".format(cursor)
            response = requests.get(url,
                                    auth=oauth)
            try:
                with open('data/processed/{}_friends/{}_friends_{}_{}.csv'.format(user_type,user_type,datetime,n_group), 'a') as f: 
                    for friend_id in response.json()['ids']:
                        f.write(str(user_id) + "," + str(friend_id) + "\n")
            except:
                print(user_id, response.json())
                break
            cursor = response.json()['next_cursor']
            
if __name__ == "__main__":
    if len(sys.argv) == 1:
        get_friends(seed_users + retweeters_users, n_seeds = len(seed_users))
    
    elif sys.argv[1] == "seeds":
        print("Getting seeds friends")
        get_friends(seed_users, n_seeds = len(seed_users), oauth = oauth_seed, datetime = time.strftime("%y%m%d%H"))
        
    elif sys.argv[1] == "retweeters":
        print("Getting retweeters friends")
        n_group = int(sys.argv[2])
        oauth = oauths[n_group]
        n_rters = len(retweeters_users)
        n_per_group = math.ceil(n_rters/len(oauths))
        
        get_friends(retweeters_users[n_group*n_per_group: (n_group+1)*n_per_group], n_seeds = 0,
                      oauth=oauth,
                      n_group = n_group)

    

    