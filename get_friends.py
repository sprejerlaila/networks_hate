import time
import pandas as pd
import requests
from requests_oauthlib import OAuth1
from accessPoints_Sprejer import TwitterAuth53 as auth


users = list(pd.read_csv("seed_users.csv").user.values)

oauth = OAuth1(auth.consumer_key,
               auth.consumer_secret,
               auth.access_token,
               auth.access_token_secret)


def get_friends(screen_names_list):
    times = [] # Control not exceeding the rate limit
    
    for screen_name in screen_names_list:
        print(screen_name)
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
            "screen_name={}".format(screen_name) + "&count=5000" + "&cursor={}".format(cursor)
            response = requests.get(url,
                                    auth=oauth)

            with open('data/processed/seed_friends/friends_{}_{}.csv'.format(screen_name,time.strftime("%y%m%d")), 'a') as f: 
                for friend_id in response.json()['ids']:
                    f.write("%s\n" % friend_id)
                        
            cursor = response.json()['next_cursor']
            
if __name__ == "__main__":
    get_friends(users)

    

    