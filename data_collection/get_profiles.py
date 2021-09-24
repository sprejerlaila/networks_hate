#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 10:05:41 2020

@author: lailasprejer
"""
import time
import datetime as dt
import os
import sys
import json
import pandas as pd
import requests
from requests_oauthlib import OAuth1
from accessPoints_nate import TwitterAuth52 as auth
from accessPoints_nate import TwitterAuth78 as auth_sf
from accessPoints_nate import TwitterAuth80 as auth_rf

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

def get_profiles(user_id_list, user_type, Oauth=oauth):
    times = [] # Control not exceeding the rate limit

    for user_id in user_id_list:
        print("id: ",user_id)
        
        if len(times) >= 900: # if 900 requests were already done
            if times[-1] - times[0] < 900: # check not exceding the rate limit
                print("waiting the needed time before continuing")
                time.sleep(910-(times[-1] - times[0])) # wait the rest of the 15 minutes
            times = times[1:] # remove the initial time 
                    
        times.append(time.time()) # adding time of the new request
        
        url = "https://api.twitter.com/1.1/users/show.json?" + \
        "user_id={}".format(user_id) + "&include_entities=true"
        
        response = requests.get(url, auth=Oauth)
        
        if 'errors' in response.json():
            er = response.json()['errors'][0]['code']
            if er == 88:
                print("Rate limit exceeded")
                time.sleep(900)
                times = []
                response = requests.get(url, auth=Oauth)
            else:
                print('Error: ', response.json())
                with open('data/profiles/collected_profiles/error_{}_{}_profiles_{}.csv'.format(er, user_type, time.strftime("%y%W")), 'a') as f:
                    f.write("id_%s\n" % user_id)
                continue


        try:
            with open('data/profiles/raw/{}_profiles_{}.json'.format(user_type, time.strftime("%y%W")), 'a') as f: 
                json.dump(response.json(), f)
                f.write('\n')

            with open('data/profiles/collected_profiles/collected_{}_profiles_{}.csv'.format(user_type, time.strftime("%y%W")), 'a') as f:
                f.write("id_%s\n" % user_id)
        except:
            with open('data/profiles/collected_profiles/error_{}_profiles_{}.csv'.format(user_type, time.strftime("%y%W")), 'a') as f:
                f.write("id_%s\n" % user_id)
            continue
                        
if __name__ == "__main__":
    ### Collect seed, retweeters, seed_followers o retweeters followers as specified

    ### Seed profiles are collected weekly
    if sys.argv[1] == "seeds": 
        seed_users = list(pd.read_csv("data/seed_users.csv").user_id.values)
        if 'seed_profiles_{}.json'.format(time.strftime("%y%W")) not in os.listdir('data/profiles'):
            get_profiles(seed_users, "seed")

    ### All other profiles are collected once
    
    collected_ids = []
    files = os.listdir('data/profiles/collected_profiles/')
    for f in files:
        try:
            with open('data/profiles/collected_profiles/{}'.format(f)) as file:
                collected_ids += file.read().splitlines()
        except:
            pass
    collected_ids = [str(x) for x in collected_ids]
    print("Number of collected users:",len(collected_ids))

    if sys.argv[1] == "retweeters":
        retweeters_users = pd.read_csv("data/processed/retweeters_users.csv").user_id.values
        retweeters_users_cc = pd.read_csv("data/processed/retweeters_users_cc.csv").user_id.values
        retweeters_users = set(list(retweeters_users) + list(retweeters_users_cc))
        del retweeters_users_cc

        print("Total number of retweeters", len(retweeters_users))
        retweeters_users = [x.replace("id_","") for x in retweeters_users if x not in collected_ids]
        print("Left to collect: ",len(retweeters_users))

        get_profiles(retweeters_users, "retweeters")
            
    elif sys.argv[1] == "seed_followers": 
        ### Because there is a huge number of followers, can't know when this code is
        ### going to end. Therefore, when it ends, just re-read files and collect missing ids
        while True:
            files = os.listdir("data/processed/seed_followers/")
            ids_to_collect = set()
            for f in files:
                try:
                    this_fols = pd.read_csv("data/processed/seed_followers/{}".format(f)).follower.values
                    this_fols = set(list(this_fols)) - set(collected_ids)
                    ids_to_collect = ids_to_collect.union(this_fols)
                except:
                    pass
            del this_fols
            
            ids_to_collect = [x.replace("id_","") for x in ids_to_collect]
            print('left to collect: ', len(ids_to_collect))

            if len(ids_to_collect) > 0:
               try:
                   get_profiles(ids_to_collect, "seed_followers", oauth_sf)
               except:
                   time.sleep(900)
                   continue
    
    elif sys.argv[1] == "retweeters_followers":
        while True:
            files = os.listdir("data/processed/retweeters_followers/")
            ids_to_collect = set()
            for f in files:
                try:
                    this_fols = pd.read_csv("data/processed/retweeters_followers/{}".format(f)).follower.values
                    this_fols = set(list(this_fols)) - set(collected_ids)
                    ids_to_collect = ids_to_collect.union(this_fols)
                except:
                    pass
            del this_fols
            
            ids_to_collect = [x.replace("id_","") for x in ids_to_collect]
            print('left to collect: ', len(ids_to_collect))
            
            if len(ids_to_collect) > 0:
                try:
                    get_profiles(ids_to_collect, "retweeters_followers", oauth_rf) 
                except:
                    time.sleep(900)
                    continue
    
