import pandas as pd
import json
import time

    
def tidy_tweets(raw_tweets):
    id_list = []
    screen_name_list = []

    text_list = []
    in_reply_to_user_id, in_reply_to_status, in_reply_to_screen_name = [], [], []
    
    rt_screen_name_list, rt_id_list = [], []
    qt_screen_name_list, qt_id_list, qt_status_list  = [], [], []
    
    mentions_list = []

    datetime = []
    location = []

    retweet_count = []
    favorite_count = []

    for idx, tweet in enumerate(raw_tweets):       
        tweet = json.loads(tweet)
        id_list.append(tweet['id'])
        
        screen_name = tweet["user"]['screen_name']
        screen_name_list.append(screen_name)

        rp_user_id = tweet["in_reply_to_user_id"]
        rp_screen_name = tweet["in_reply_to_screen_name"]
        rp_status = tweet["in_reply_to_status_id"]

        t = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))
        datetime.append(t)

        location.append(tweet['place'])
        retweet_count.append(tweet['retweet_count']) #TODO replace with rt fav count when available
        favorite_count.append(tweet['favorite_count']) #TODO replace with rt fav count when available
        
        text = tweet['text'] if "text" in tweet else tweet['full_text']
        
        rt_screen_name, rt_id, qt_id, qt_screen_name, qt_status = None, None, None, None, None
        
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
        
        text_list.append(text)
        in_reply_to_status.append(rp_status)
        in_reply_to_user_id.append(rp_user_id)
        in_reply_to_screen_name.append(rp_screen_name)
        rt_screen_name_list.append(rt_screen_name)
        rt_id_list.append(rt_id)
        qt_id_list.append(qt_id)
        qt_screen_name_list.append(qt_screen_name)
        qt_status_list.append(qt_status)
        
        mentions_list.append(mentions)
        
    data = pd.DataFrame({
        "id" : id_list,
        "screen_name": screen_name_list,
        "text": text_list,
        "rt_from_screen_name": rt_screen_name_list,
        "rt_from_id": rt_id_list,
        "qt_from_screen_name": qt_screen_name_list,
        'qt_status': qt_status_list,
        "in_reply_to_screen_name": in_reply_to_screen_name,
        "in_reply_to_status": in_reply_to_status,
        "mentions": mentions_list,
        "datetime":datetime})
    
    return data

users = list(pd.read_csv("seed_users.csv").user.values)

class process_tweets():
    def __init__(self, day_to_process):
        self.day_to_process = day_to_process
        with open('data/seed_tweets/seed_tweets_{}.json'.format(day_to_process)) as json_data:
            stream_tweets = json_data.readlines()
        stream_tweets = tidy_tweets(stream_tweets)
        
        with open('data/seed_tweets/rest_tweets_{}.json'.format(day_to_process)) as json_data:
            rest_tweets = json_data.readlines()
        rest_tweets = tidy_tweets(rest_tweets)

        
        self.tweets = pd.concat([stream_tweets, rest_tweets[~rest_tweets.id.isin(stream_tweets.id)]]).reset_index(drop=True)
        self.extract_seed_tweets()
        self.extract_seed_retweets()
        
    
        
    def extract_seed_tweets(self):
        print("Extracting seed tweets, saving to data/processed/seed_tweets/")
        seed_tweets = self.tweets[self.tweets.screen_name.isin(users)]
        
        # Write full dataframe
        seed_tweets.to_csv("data/processed/seed_tweets/processed_seed_tweets.csv", index=False, mode='a')
        
        
        # Keep a list of seed tweets ids
        with open('data/processed/seed_tweets/seed_tweets_ids.csv', 'a') as f: 
            for tweet_id in seed_tweets.id.values:
                    f.write("%s\n" % tweet_id)
        
    def extract_seed_retweets(self):
        print("Extracting seed retweets, saving to data/processed/seed_retweets/")
        with open('data/processed/seed_tweets/seed_tweets_ids.csv') as file:
            ids = file.read().splitlines()
        
        seed_reweets = self.tweets[self.tweets.rt_from_id.isin(ids)]
        seed_reweets.to_csv("data/processed/seed_retweets/processed_seed_retweets.csv", index=False, mode='a')
    
    
    
    
    
    