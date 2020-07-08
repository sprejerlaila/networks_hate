import sys
import os
import math
import time
import pandas as pd
import requests
from requests_oauthlib import OAuth1
from accessPoints_Sprejer import TwitterAuth83 as auth_seed0
from accessPoints_Sprejer import TwitterAuth84 as auth_seed1
from accessPoints_Sprejer import TwitterAuth85 as auth_seed2
from accessPoints_Sprejer import TwitterAuth41 as auth0
from accessPoints_Sprejer import TwitterAuth42 as auth1
from accessPoints_Sprejer import TwitterAuth43 as auth2
from accessPoints_Sprejer import TwitterAuth44 as auth3
from accessPoints_Sprejer import TwitterAuth45 as auth4
from accessPoints_Sprejer import TwitterAuth138 as auth5
from accessPoints_Sprejer import TwitterAuth139 as auth6
from accessPoints_Sprejer import TwitterAuth140 as auth7
from accessPoints_Sprejer import TwitterAuth141 as auth8
from accessPoints_Sprejer import TwitterAuth142 as auth9
from accessPoints_Sprejer import TwitterAuth143 as auth10
from accessPoints_Sprejer import TwitterAuth144 as auth11
from accessPoints_Sprejer import TwitterAuth145 as auth12
from accessPoints_Sprejer import TwitterAuth146 as auth13
from accessPoints_Sprejer import TwitterAuth147 as auth14

oauth_seed0 = OAuth1(auth_seed0.consumer_key, auth_seed0.consumer_secret, auth_seed0.access_token, auth_seed0.access_token_secret)
oauth_seed1 = OAuth1(auth_seed1.consumer_key, auth_seed1.consumer_secret, auth_seed1.access_token, auth_seed1.access_token_secret)
oauth_seed2 = OAuth1(auth_seed2.consumer_key, auth_seed2.consumer_secret, auth_seed2.access_token, auth_seed2.access_token_secret)
oauths_seed = [oauth_seed0, oauth_seed1, oauth_seed2]


oauth0 = OAuth1(auth0.consumer_key, auth0.consumer_secret, auth0.access_token, auth0.access_token_secret)

oauth1 = OAuth1(auth1.consumer_key, auth1.consumer_secret, auth1.access_token, auth1.access_token_secret)

oauth2 = OAuth1(auth2.consumer_key, auth2.consumer_secret, auth2.access_token, auth2.access_token_secret)

oauth3 = OAuth1(auth3.consumer_key, auth3.consumer_secret, auth3.access_token, auth3.access_token_secret)

oauth4 = OAuth1(auth4.consumer_key, auth4.consumer_secret, auth4.access_token, auth4.access_token_secret)

oauth5 = OAuth1(auth5.consumer_key, auth5.consumer_secret, auth5.access_token, auth5.access_token_secret)

oauth6 = OAuth1(auth6.consumer_key, auth6.consumer_secret, auth6.access_token, auth6.access_token_secret)

oauth7 = OAuth1(auth7.consumer_key, auth7.consumer_secret, auth7.access_token, auth7.access_token_secret)

oauth8 = OAuth1(auth8.consumer_key, auth8.consumer_secret, auth8.access_token, auth8.access_token_secret)

oauth9 = OAuth1(auth9.consumer_key, auth9.consumer_secret, auth9.access_token, auth9.access_token_secret)

oauth10 = OAuth1(auth10.consumer_key, auth10.consumer_secret, auth10.access_token, auth10.access_token_secret)

oauth11 = OAuth1(auth11.consumer_key, auth11.consumer_secret, auth11.access_token, auth11.access_token_secret)

oauth12 = OAuth1(auth12.consumer_key, auth12.consumer_secret, auth12.access_token, auth12.access_token_secret)

oauth13 = OAuth1(auth13.consumer_key, auth13.consumer_secret, auth13.access_token, auth13.access_token_secret)

oauth14 = OAuth1(auth14.consumer_key, auth14.consumer_secret, auth14.access_token, auth14.access_token_secret)

oauths = [oauth0, oauth1, oauth2, oauth3, oauth4, oauth5, oauth6, oauth7, oauth8, oauth9, oauth10, oauth11, oauth12, oauth13, oauth14]


def get_followers(user_id_list, n_seeds, oauth=oauth0, n_group = 0, datetime=time.strftime("%y%m%d")):
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
                with open('data/processed/{}_followers/{}_followers_{}_{}.csv'.format(user_type, user_type, datetime,n_group), 'a') as f: 
                    for follower_id in response.json()['ids']:
                        f.write(str(user_id) + "," + str(follower_id) + "\n")
                if cursor == -1:
                    with open('data/collected_followers_ids.csv', 'a') as f:
                        f.write("%s\n" % user_id)
            except:
                print(user_id, response.json())
                break
            cursor = response.json()['next_cursor']
        
if __name__ == "__main__":
    seed_users = list(pd.read_csv("data/seed_users.csv").user_id.values)
    print(type(seed_users[0])) 
    if sys.argv[1] == "seeds":
        print("Getting seeds followers")
        n_group = int(sys.argv[2])
        oauth = oauths_seed[n_group]
        n_rters = len(seed_users)
        n_per_group = math.ceil(n_rters/len(oauths_seed))

        get_followers(seed_users[n_group*n_per_group: (n_group+1)*n_per_group], n_seeds = len(seed_users),
                oauth=oauth,
                n_group = n_group) 

    elif sys.argv[1] == "retweeters":
        print("Getting new retweeters followers")
        
        if 'collected_followers_ids.csv' in os.listdir('data/'):
            with open('data/collected_followers_ids.csv') as file:
                collected_ids = file.read().splitlines()
        else:
            collected_ids = []
 
        all_retweeters = pd.read_csv("data/retweeters_users.csv")
        print(len(all_retweeters))
        # get only new retweeters
        new_retweeters = all_retweeters[~all_retweeters.user_id.isin(collected_ids)].user_id.values
            
        if len(new_retweeters) == 0:
            print('No more users to collect')
        
	else:
            print('collecting %i users' %len(new_retweeters))
            n_group = int(sys.argv[2])
            oauth = oauths[n_group]
            n_rters = len(new_retweeters)
            n_per_group = math.ceil(n_rters/len(oauths))
            
            get_followers(new_retweeters[n_group*n_per_group: (n_group+1)*n_per_group], n_seeds = 0,
                          oauth=oauth,
                          n_group = n_group)
            
            
            
            
