import time
import pandas as pd
import requests
from accessPoints_Sprejer import TwitterAuth52 as auth
from requests_oauthlib import OAuth1


oauth = OAuth1(auth.consumer_key,
               auth.consumer_secret,
               auth.access_token,
               auth.access_token_secret)


def structure_tweets(results):
        id_list=[tweet['id'] for tweet in results]
        
        data=pd.DataFrame(id_list,columns=['id'])
        data['screen_name'] =[tweet['user']['screen_name'] for tweet in results]

        data["text"]= [tweet['text'] for tweet in results]
        
        data["datetime"]=[time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')) for tweet in results]
        
        data["Location"]=[tweet['place'] for tweet in results]
    
        return data

class get_user_tweets():
    
    def __init__(self, user, day):
        self.user = user
        self.day = day
        self.results = []
        self.get_timeline()
        self.get_mentions()
        self.results = pd.concat(self.results)

        
    def get_timeline(self):
        response = requests.get("https://api.twitter.com/1.1/statuses/user_timeline.json",
                        params = {"screen_name": self.user},
                        auth=oauth)
        
        self.results.append(structure_tweets(response.json()))


    def get_mentions(self):
        next_page_url = "https://api.twitter.com/1.1/search/tweets.json"
        while True:
            response = requests.get(next_page_url,
                                params = {"q": self.user, "count":200},
                                auth=oauth)

            response = response.json()

            self.results.append(structure_tweets(response['statuses']))
            if response['statuses'][-1]['created_at'].split()[2] != self.day:
                break    
            next_page_url = "https://api.twitter.com/1.1/search/tweets.json" \
            + response['search_metadata']['next_results']
