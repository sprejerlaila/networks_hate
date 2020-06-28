#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 10:05:41 2020

@author: lailasprejer
"""
import time
import os
import sys
import json
import pandas as pd
import requests
from requests_oauthlib import OAuth1
from accessPoints_Sprejer import TwitterAuth52 as auth
from accessPoints_Sprejer import TwitterAuth78 as auth_sf
from accessPoints_Sprejer import TwitterAuth80 as auth_rf

oauth = OAuth1(auth.consumer_key,
               auth.consumer_secret,
               auth.access_token,
               auth.access_token_secret)

oauth_sf = OAuth1(auth_sf.consumer_key,
               auth_sf.consumer_secret,
               auth_sf.access_token,
               auth_sf.access_token_secret)

oauth_rf = OAuth1(auth_rf.consumer_key,
               auth_rf.consumer_secret,
               auth_rf.access_token,
               auth_rf.access_token_secret)

def get_profiles(screen_names_list, user_type,Oauth=oauth):
    times = [] # Control not exceeding the rate limit
    
    for idx, user_id in enumerate(screen_names_list):
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
                                    auth=Oauth)

        try:
            with open('data/profiles/{}_profiles_{}.json'.format(user_type, time.strftime("%y%W")), 'a') as f: 
                json.dump(response.json(), f)
                f.write('\n')

            with open('data/profiles/collected_{}_profiles.csv'.format(user_type, time.strftime("%y%W")), 'a') as f:
                f.write("%s\n" % user_id)
        except:
            continue
                        
if __name__ == "__main__":
    if sys.argv[1] == "seeds":
        seed_users = list(pd.read_csv("data/seed_users.csv").user_id.values)
        if 'seed_profiles_{}.json'.format(time.strftime("%y%W")) not in os.listdir('data/profiles'):
            get_profiles(seed_users, "seed")
    
    elif sys.argv[1] == "retweeters":
        retweeters_users = list(pd.read_csv("data/retweeters_users.csv").user_id.values)

        if 'retweeters_profiles_{}.json'.format(time.strftime("%y%W")) in os.listdir('data/profiles'):    
            with open('data/profiles/retweeters_profiles_{}.json'.format(time.strftime("%y%W"))) as json_data:
                n_retweeters_profiles = len(json_data.readlines())
        
            if n_retweeters_profiles >= len(retweeters_users):
                retweeters_users = []
            else:
                retweeters_users = retweeters_users[-(len(retweeters_users) - n_retweeters_profiles):]
        get_profiles(retweeters_users, "retweeters")
            
    elif sys.argv[1] == "seed_followers":
        while True:
            seed_followers_users = pd.read_csv("data/processed/seed_followers/seed_daily_followers_200618.csv")    
            print(len(seed_followers_users))
            if 'collected_seed_followers_profiles.csv' in os.listdir('data/profiles/'):
                with open('data/profiles/collected_seed_followers_profiles.csv') as file:
                    collected_ids = file.read().splitlines()
            
                seed_followers_users = list(seed_followers_users[~seed_followers_users.follower.isin(collected_ids)].follower.values)
            print(len(seed_followers_users))
            if len(seed_followers_users) > 0:
                try:
                    get_profiles(seed_followers_users, "seed_followers", oauth_sf)
                except:
                    time.sleep(900)
                    continue
            else:
                break
    
    elif sys.argv[1] == "retweeters_followers":
        while True:
            retweeters_followers_users = pd.read_csv("data/processed/retweeters_followers/retweeters_daily_followers_200619.csv")
            if 'collected_retweeters_followers_profiles.csv' in os.listdir('data/profiles/'):
                with open('data/profiles/collected_retweeters_followers_profiles.csv') as file:
                    collected_ids = file.read().splitlines()
                retweeters_followers_users = list(retweeters_followers_users[~retweeters_followers_users.follower.isin(collected_ids)].follower.values)
            if len(retweeters_followers_users) > 0:
                try:
                    get_profiles(retweeters_followers_users, "retweeters_followers", oauth_rf) 
                except:
                    time.sleep(900)
                    continue
            else:
                break
    
