#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 10:14:36 2020

@author: lailasprejer
"""

import pandas as pd
import time
import os
import sys
import math
import json
import botometer


from accessPoints_Sprejer_Botometer import TwitterAuth76 as auth0
from accessPoints_Sprejer_Botometer import TwitterAuth77 as auth1

auths = [auth0, auth1]
rapidapi_keys = ["XXX", "XXX"]

def get_botometer(user_id_list, oauth, rapidapi, n_group = 0):
    twitter_app_auth = {
    'consumer_key': oauth.consumer_key,
    'consumer_secret': oauth.consumer_secret,
    'access_token': oauth.access_token,
    'access_token_secret': oauth.access_token_secret,
  }
    
    times = []
    total_times = []
    
    for idx, user_id in enumerate(user_id_list):
        
        print(n_group, idx, user_id)
    
        bom = botometer.Botometer(wait_on_ratelimit=False,
                          rapidapi_key=rapidapi,
                          **twitter_app_auth)
        
        if len(times) == 180: # if 180 requests were already done
                if times[-1] - times[0] < 900: # check not exceding the rate limit
                    print("waiting the needed time before continuing")
                    time.sleep(901-(times[-1] - times[0])) # wait the rest of the 15 minutes
                times = times[1:] # remove the initial time 


        times.append(time.time())
        total_times.append(time.time())
        
        try:
            # Save data in json
            with open('data/botometer/botometer_{}.json'.format(n_group), 'a') as tf:
                response = bom.check_account(user_id)
                json.dump(response, tf)
                tf.write('\n')
                
            # Keep track of collected ids
            with open('data/botometer/collected_botometer_ids.csv', 'a') as f:
                f.write("%s\n" % user_id)
        
        except Exception as e:
            print('error')
            print(e)
            try:
                # Detect deleted / bloqued users to avoid collecting them again
                if eval(str(e))[0]['code']==34:
                    print('nonexistent user')
                    with open('data/botometer/nonexistent_botometer_ids.csv', 'a') as f:
                        f.write("%s\n" % user_id)
                
                # Rate limit error -- wait and try again 
                if eval(str(e))[0]['code']==88:
                    print('error, waiting 15 minutes')
                    time.sleep(900)

            except:
                print('other error ', e)
                with open('data/botometer/error_botometer_ids.csv', 'a') as f:
                    f.write("%s\n" % user_id) 
            
            # Restart botometer
            bom = botometer.Botometer(wait_on_ratelimit=False,
                    rapidapi_key=rapidapi,
                    **twitter_app_auth)
        
if __name__ == "__main__":
    if 'collected_botometer_ids.csv' in os.listdir('data/botometer'):
        with open('data/botometer/collected_botometer_ids.csv') as file:
            collected_ids = file.read().splitlines()
    if 'nonexistent_botometer_ids.csv' in os.listdir('data/botometer'):
        with open('data/botometer/nonexistent_botometer_ids.csv') as file:
            collected_ids += file.read().splitlines()

    if 'error_botometer_ids.csv' in os.listdir('data/botometer'):
        with open('data/botometer/error_botometer_ids.csv') as file:
            collected_ids += file.read().splitlines()
            
    else:
        collected_ids = []
            
    ids1 = pd.read_csv('data/retweeters_users.csv')
    ids2 = pd.read_csv('data/retweeters_users_cc.csv')
    ids = pd.concat([ids1,ids2]).drop_duplicates('user_id').reset_index(drop=True)
    ids = ids[~ids.user_id.isin(collected_ids)].user_id.values
    
    print("IDs left to collect: ",len(ids))
    
    # Paralelize collection
    n_group = int(sys.argv[1])
    n_per_group = math.ceil(len(ids)/len(auths))
    
    print("    Using rapid key: ", rapidapi_keys[n_group])
    print("    Using twitter key: ", auths[n_group].consumer_key)
    
    get_botometer(ids[n_group*n_per_group: (n_group+1)*n_per_group], \
                  oauth=auths[n_group], \
                  rapidapi = rapidapi_keys[n_group], \
                      n_group = n_group)
