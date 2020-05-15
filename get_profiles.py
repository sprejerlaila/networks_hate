#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 10:05:41 2020

@author: lailasprejer
"""
import time
import os
import json
import pandas as pd
import requests
from requests_oauthlib import OAuth1
from accessPoints_Sprejer import TwitterAuth54 as auth


oauth = OAuth1(auth.consumer_key,
               auth.consumer_secret,
               auth.access_token,
               auth.access_token_secret)


def get_profiles(screen_names_list, n_seeds):
    times = [] # Control not exceeding the rate limit
    
    for idx, user_id in enumerate(screen_names_list):
        user_type = "seed" if idx < n_seeds else "retweeters"
        print("id: ",user_id)
        
        if len(times) == 900: # if 900 requests were already done
            if times[-1] - times[0] < 900: # check not exceding the rate limit
                print("waiting the needed time before continuing")
                time.sleep(900-(times[-1] - times[0])) # wait the rest of the 15 minutes
            times = times[1:] # remove the initial time 
                    
        times.append(time.time()) # adding time of the new request
        url = "https://api.twitter.com/1.1/users/show.json?" + \
        "user_id={}".format(user_id) + "&include_entities=true"# + "&cursor={}".format(cursor)
        response = requests.get(url,
                                auth=oauth)

        with open('data/{}_profiles.json'.format(user_type), 'a') as f: 
            json.dump(response.json(), f)
            f.write('\n')
                        
if __name__ == "__main__":
    seed_users = list(pd.read_csv("data/seed_users.csv").user_id.values)
    retweeters_users = list(pd.read_csv("data/retweeters_users.csv").user_id.values)

    if 'seed_profiles.json' in os.listdir('data/'):
        with open('data/seed_profiles.json') as json_data:
            n_seed_profiles = len(json_data.readlines())
            
        if n_seed_profiles >= len(seed_users):
            seed_users = []
        else:
            seed_users = seed_users[-(len(seed_users) - n_seed_profiles):]
    
    
    if 'retweeters_profiles.json' in os.listdir('data/'):    
        with open('data/retweeters_profiles.json') as json_data:
            n_retweeters_profiles = len(json_data.readlines())
        
        if n_retweeters_profiles >= len(retweeters_users):
            retweeters_users = []
        else:
            retweeters_users = retweeters_users[-(len(retweeters_users) - n_retweeters_profiles):]
            
    if len(seed_users + retweeters_users) == 0:
        print("No new users added")
    
    else:
        get_profiles(seed_users + retweeters_users, n_seeds = len(seed_users))
        
    
    
    
    
    
    