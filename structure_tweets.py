import pandas as pd
import json
import time


def structure_results(results):
    id_list = []
    screen_name_list = []

    text_list = []
    in_reply_to_user_id, in_reply_to_status, in_reply_to_screen_name = [], [], []
    
    rt_from_screen_name = []
    qt_screen_name_list, qt_id_list, qt_status_list  = [], [], []
    
    mentions_list = []

    datetime = []
    location = []

    retweet_count = []
    favorite_count = []

    for idx, tweet in enumerate(results):       
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
        
        text = tweet['text']
        
        rt_screen_name, qt_id, qt_screen_name, qt_status = None, None, None, None
        
        mentions = set([x['screen_name'] for x in tweet['entities']['user_mentions']])
        
        if 'retweeted_status' in tweet: # It is a retweet 
            text = tweet['retweeted_status']['text']
            try:
                text = tweet['retweeted_status']['extended_tweet']['full_text']
                mentions = set([x['screen_name'] for x in tweet['retweeted_status']['extended_tweet']['entities']['user_mentions']])
            except:
                pass
            rt_screen_name = tweet['retweeted_status']['user']['screen_name']

        if 'quoted_status' in tweet: # In reply to tweet data
            qt_id = tweet["quoted_status"]["user"]["id"]
            qt_screen_name = tweet["quoted_status"]["user"]["screen_name"]
            qt_status = tweet["quoted_status"]["text"]
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
        rt_from_screen_name.append(rt_screen_name)
        qt_id_list.append(qt_id)
        qt_screen_name_list.append(qt_screen_name)
        qt_status_list.append(qt_status)
        
        mentions_list.append(mentions)
        
    data = pd.DataFrame({
        "id" : id_list,
        "screen_name": screen_name_list,
        "text": text_list,
        "rt_from_screen_name": rt_from_screen_name,
        "qt_from_screen_name": qt_screen_name_list,
        'qt_status': qt_status_list,
        "in_reply_to_screen_name": in_reply_to_screen_name,
        "in_reply_to_status": in_reply_to_status,
        "mentions": mentions_list,
        "datetime":datetime})
    return data