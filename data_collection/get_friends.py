import sys
import os
import math
import time
import pandas as pd
import datetime as dt
import requests
from requests_oauthlib import OAuth1
from accessPoints_nate import TwitterAuth53 as auth_seed0
from accessPoints_nate import TwitterAuth54 as auth_seed1
from accessPoints_nate import TwitterAuth41 as auth0


oauth_seed0 = OAuth1(auth_seed0.consumer_key, auth_seed0.consumer_secret, auth_seed0.access_token, auth_seed0.access_token_secret)
oauth_seed1 = OAuth1(auth_seed1.consumer_key, auth_seed1.consumer_secret, auth_seed1.access_token, auth_seed1.access_token_secret)
oauths_seed = [oauth_seed0, oauth_seed1]

oauth0 = OAuth1(auth0.consumer_key, auth0.consumer_secret, auth0.access_token, auth0.access_token_secret)


oauths = [oauth0]


def get_friends(user_type, user_id_list, oauth=oauth0, n_group = 0, datetime=time.strftime("%y%m%d")):
    times = [] # Control not exceeding the rate limit
    for user_id in user_id_list:
        print("Collecting user_id: ", user_id)
        
        if user_type  == 'retweeters' and int(dt.datetime.now().strftime("%H")) == 2: # Break because new collection will start
            print('Its a brand new day')
            break

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
            response = requests.get(url, auth=oauth)

            if 'errors' in response.json():
                er = response.json()['errors'][0]['code']
                if er == 88:
                    print("Rate limit exceeded. Waiting the time limit")
                    cursor = -1
                    time.sleep(900)
                    times = []
                    response = requests.get(url, auth=oauth) ###dedlete?  

                else:
                    print('Error: ', response.json())
                    with open('data/processed/collected_friends/error_{}_{}_profiles_{}.csv'.format(er, user_type, time.strftime("%y%W")), 'a') as f:
                        f.write("id_%s\n" % user_id)
                    cursor = 0
                    continue
            try:
                with open('data/processed/{}_friends/{}_friends_{}_{}.csv'.format(user_type,user_type,datetime,n_group), 'a') as f: 
                    for friend_id in response.json()['ids']:
                        f.write("id_" + str(user_id) + "," + "id_" + str(friend_id) + "\n")
                
                cursor = response.json()['next_cursor']
                
                if cursor == 0:
                    with open('data/processed/collected_friends/collected_{}_friends_ids_{}.csv'.format(user_type, n_group), 'a') as f:
                        f.write("id_%s\n" % user_id)
            except:
                print(user_id, response.json())
                with open('data/processed/collected_friends/error_{}_profiles_{}.csv'.format(user_type, time.strftime("%y%W")), 'a') as f:
                        f.write("id_%s\n" % user_id)
                break
            
if __name__ == "__main__":
    seed_users = list(pd.read_csv("data/seed_users.csv").user_id.values)
    
    if sys.argv[1] == "seeds":
        print("Getting seeds friends")

        n_group = int(sys.argv[2])
        oauth = oauths_seed[n_group]
        n_rters = len(seed_users)
        n_per_group = math.ceil(n_rters/len(oauths_seed))
  
        get_friends(
            user_type = "seed",
            user_id_list = seed_users[n_group*n_per_group: (n_group+1)*n_per_group],
            oauth=oauth,
            n_group = n_group)

    elif sys.argv[1] == "retweeters":
        print("Getting retweeters friends")

        for retweeters_file in ['retweeters_users.csv','retweeters_users_cc.csv']:

            files = os.listdir('data/processed/collected_friends')
            collected_ids = []
            for f in files:
                try:
                    with open('data/processed/collected_friends/{}'.format(f)) as file:
                        collected_ids += file.read().splitlines()
                except:
                    pass
            collected_ids = [str(x) for x in collected_ids]
            
            all_retweeters = pd.read_csv("data/processed/{}".format(retweeters_file))
            all_retweeters['user_id'] = all_retweeters['user_id'].astype(str)
            
            print('All_retweeters:', len(all_retweeters))
            print("Number of collected users:",len(collected_ids))
            
            # get only new retweeters
            new_retweeters = all_retweeters[~all_retweeters.user_id.isin(collected_ids)].user_id.values
            new_retweeters = [x.replace("id_","") for x in new_retweeters]

            del collected_ids
            del all_retweeters

            if len(new_retweeters) > 0:
                print('collecting %i users' %len(new_retweeters))
                n_group = int(sys.argv[2])
                oauth = oauths[n_group]
                n_rters = len(new_retweeters)
                n_per_group = math.ceil(n_rters/len(oauths))
                print(new_retweeters[:10])
                get_friends(
                    user_type = "retweeters",
                    user_id_list = new_retweeters[n_group*n_per_group: (n_group+1)*n_per_group],
                    oauth=oauth,
                    n_group = n_group)
            
            print("Done with small influencers. Starting Charlie Kirk and Candace Owens")
            time.sleep(900)  

    

    
