import pandas as pd
import json
import time
import os
import datetime as dt
import re

    
def tidy_tweets(file_name):
    seed_tweets_dict = {}
    screen_name_dict = {}
    if "seed_tweets.csv" in os.listdir('data/processed/seed_tweets/'):
        seed_tweets = pd.read_csv('data/processed/seed_tweets/seed_tweets.csv')
        for idx, row in seed_tweets.iterrows():
            seed_tweets_dict[row['text']] = [row['screen_name'], row['id']]
            screen_name_dict[row['screen_name']] = row['id']
    print('done with dicts')
    id_list = []
    screen_name_list = []
    user_id_list = []

    text_list = []
    in_reply_to_user_id, in_reply_to_status, in_reply_to_screen_name = [], [], []
    
    rt_screen_name_list, rt_id_list, rt_type_list = [], [], []
    qt_screen_name_list, qt_id_list, qt_status_list  = [], [], []
    
    mentions_list = []

    datetime = []
    # location = []

    # retweet_count = []
    # favorite_count = []
    
    with open(file_name) as json_data:
        for idx, tweet in enumerate(json_data):
            
            tweet = json.loads(tweet)
            
            id_list.append(tweet['id'])

            screen_name = tweet["user"]['screen_name']
            screen_name_list.append(screen_name)
            user_id = tweet["user"]['id']
            user_id_list.append(user_id)

            rp_user_id = tweet["in_reply_to_user_id"]
            rp_screen_name = tweet["in_reply_to_screen_name"]
            rp_status = tweet["in_reply_to_status_id"]

            t = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))
            datetime.append(t)

            #location.append(tweet['place'])
            #retweet_count.append(tweet['retweet_count']) #TODO replace with rt fav count when available
            #favorite_count.append(tweet['favorite_count']) #TODO replace with rt fav count when available

            text = tweet['text'] if "text" in tweet else tweet['full_text']

            rt_screen_name, rt_id, rt_type, qt_id, qt_screen_name, qt_status = None, None, None, None, None, None

            mentions = set([x['screen_name'] for x in tweet['entities']['user_mentions']])

            if 'retweeted_status' in tweet: # It is a retweet
                text = tweet['retweeted_status']['text'] if 'text' in tweet['retweeted_status'] else tweet['retweeted_status']['full_text']
                try:
                    text = tweet['retweeted_status']['extended_tweet']['full_text']
                    mentions = set([x['screen_name'] for x in tweet['retweeted_status']['extended_tweet']['entities']['user_mentions']])
                except:
                    pass
                rt_screen_name = tweet['retweeted_status']['user']['screen_name']
                rt_id = tweet['retweeted_status']['id']
                rt_type = 'official'
                
            if 'quoted_status' in tweet: # In reply to tweet data
                qt_id = tweet["quoted_status"]["user"]["id"]
                qt_screen_name = tweet["quoted_status"]["user"]["screen_name"]
                qt_status = tweet["quoted_status"]["text"] if 'text' in tweet['quoted_status'] else tweet['quoted_status']['full_text']
                try:
                    qt_status = tweet["quoted_status"]["extended_tweet"]['full_text']

                except:
                    try:
                        qt_status = tweet["quoted_status"]["user"]["text"]
                    except:
                        pass

            if 'extended_tweet' in tweet:
                text = tweet['extended_tweet']['full_text']
                mentions = set([x['screen_name'] for x in tweet['extended_tweet']['entities']['user_mentions']])
                
            # Look for unofficial retweets
            if rt_screen_name is None and re.search(r'^(RT|Rt|rt|retweet)(?:\b\W*@(\w+)) (.*)', text):
                rt_screen_name = re.search(r'^(RT|Rt|rt|retweet)(?:\b\W*@(\w+)) (.*)', text)[2]
                rt_type = 'unofficial accredited'
                if re.search(r'^(RT|Rt|rt|retweet)(?:\b\W*@(\w+)) (.*)', text)[3] in seed_tweets_dict:
                    rt_id = seed_tweets_dict[text][1]
            
            # Look for unnoficial uncredited retweets
            if rt_screen_name is None and text in seed_tweets_dict:
                rt_screen_name = seed_tweets_dict[text][0]
                rt_id = seed_tweets_dict[text][1]
                rt_type = 'unofficial unaccredited'

            text_list.append(text)
            in_reply_to_status.append(rp_status)
            in_reply_to_user_id.append(rp_user_id)
            in_reply_to_screen_name.append(rp_screen_name)
            rt_screen_name_list.append(rt_screen_name)
            rt_id_list.append(rt_id)
            rt_type_list.append(rt_type)
            qt_id_list.append(qt_id)
            qt_screen_name_list.append(qt_screen_name)
            qt_status_list.append(qt_status)
            mentions_list.append(mentions)

    data = pd.DataFrame({
        "id" : id_list,
        "screen_name": screen_name_list,
        "user_id": user_id_list,
        "text": text_list,
        "rt_from_screen_name": rt_screen_name_list,
        "rt_from_id": rt_id_list,
        "qt_from_screen_name": qt_screen_name_list,
        'qt_status': qt_status_list,
        "in_reply_to_screen_name": in_reply_to_screen_name,
        "in_reply_to_status": in_reply_to_status,
        "mentions": mentions_list,
        "datetime":datetime,
        "rt_type": rt_type_list})

    return data


users = list(pd.read_csv("data/seed_users.csv").screen_name.values)

class process_tweets():
    def __init__(self, day_to_process):
        self.day_to_process = day_to_process

        print("> tidy stream")
        stream_tweets = tidy_tweets('data/raw/seed_tweets/stream_tweets_{}.json'.format(day_to_process))
        
        print("> tidy rest")
        rest_tweets = tidy_tweets('data/raw/seed_tweets/rest_tweets_{}.json'.format(day_to_process))

        
        print("> filtering tweets not in stream")
        self.tweets = pd.concat([stream_tweets, rest_tweets[~rest_tweets.id.isin(stream_tweets.id)]]).drop_duplicates("id").reset_index(drop=True)
        #self.tweets = rest_tweets
        self.tweets.to_csv('test.csv', index=False, mode='a')
        
        print("> extract seed")
        self.extract_seed_tweets()

        print("> extact_retweets")
        self.extract_seed_retweets()
        
    
        
    def extract_seed_tweets(self):
        print("> Extracting seed tweets df, saving to data/processed/seed_tweets/seed_tweets.csv")
        seed_tweets = self.tweets[self.tweets.screen_name.isin(users)]
        
        # Write full dataframe
        if not os.path.isfile('data/processed/seed_tweets/seed_tweets.csv'):
            seed_tweets.to_csv("data/processed/seed_tweets/seed_tweets.csv", index=False)
        else:
            seed_tweets.to_csv("data/processed/seed_tweets/seed_tweets.csv", index=False, header=False, mode='a')
        
        print("> Extracting seed tweets_id list, saving to data/seed_tweets_ids.csv")
        # Keep a list of seed tweets ids
        with open('data/seed_tweets_ids.csv', 'a') as f: 
            for tweet_id in seed_tweets.id.values:
                    f.write("%s\n" % tweet_id)
        
    def extract_seed_retweets(self):
        print("> Extracting retweets from seeds df, saving to data/processed/seed_retweets/retweets_from_seeds.csv")
        with open('data/seed_tweets_ids.csv') as file:
            ids = file.read().splitlines()
        ids = [int(i) for i in ids]

        seed_retweets = self.tweets[self.tweets.rt_from_id.isin(ids)]
        
        if not os.path.isfile('data/processed/seed_retweets/retweets_from_seeds.csv'):
            seed_retweets.to_csv("data/processed/seed_retweets/retweets_from_seeds.csv", index=False)
        else:
            seed_retweets.to_csv("data/processed/seed_retweets/retweets_from_seeds.csv", index=False, header=False, mode='a')
        
        
        print("> Extracting retweeters screen_name and id, saving to data/retweeters_users.csv")
        if 'retweeters_users.csv' in os.listdir('data/'):
            current_retweeters = pd.read_csv('data/retweeters_users.csv')[["screen_name","user_id"]]
            new_retweeters = seed_retweets[~seed_retweets.user_id.isin(current_retweeters.user_id)][["screen_name","user_id"]]
            new_retweeters = new_retweeters.drop_duplicates()
            all_retweeters = pd.concat([current_retweeters, new_retweeters]).reset_index(drop=True)

        
        else:
            all_retweeters = seed_retweets[["screen_name","user_id"]].drop_duplicates()
            
        
        all_retweeters.to_csv('data/retweeters_users.csv', index=False)

        
    
if __name__ == "__main__":
    yesterday = dt.datetime.strftime(dt.datetime.now() - dt.timedelta(1), '%y%m%d')
    #process_tweets(day_to_process=yesterday)                 
    # process_tweets(day_to_process='200525')                 
    # process_tweets(day_to_process='200526')                 
    #process_tweets(day_to_process='200527')                 
    process_tweets(day_to_process='200528')                 
    process_tweets(day_to_process='200529')                 
    process_tweets(day_to_process='200530')                 
 
    
