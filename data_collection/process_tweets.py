import pandas as pd
import json
import time
import os
import datetime as dt
import re
import wget
    
def tidy_tweets(file_name):
    '''Converts json raw tweets into tidy df'''

    ### This is to look for unattributed retweets
    seed_tweets_dict,  screen_name_dict = {}, {}
    if "seed_tweets.csv" in os.listdir('data/processed/seed_tweets/'):
        seed_tweets = pd.read_csv('data/processed/seed_tweets/seed_tweets.csv')
        for idx, row in seed_tweets.iterrows():
            seed_tweets_dict[row['text']] = [row['screen_name'], row['id'], row['user_id']]
            screen_name_dict[row['screen_name']] = row['id']
    
    id_list, datetime_list, screen_name_list, user_id_list, text_list = [], [], [], [], []
    in_reply_to_user_id_list, in_reply_to_status_id_list, in_reply_to_screen_name_list = [], [], []
    rt_screen_name_list, rt_user_id_list, rt_id_list, rt_type_list = [], [], [], []
    qt_screen_name_list, qt_id_list, qt_status_list  = [], [], []
    mentions_list, hashtags_list  = [], []
    photos_list, videos_list, gifs_list = [], [], []
    urls_list, trunc_url_list = [], []
    
    with open(file_name) as json_data:
        for idx, tweet in enumerate(json_data):
            
            try:
                tweet = json.loads(tweet)
            except:
                print('could not open line ',idx)
                continue

            id_list.append("id_" + str(tweet['id']))
            screen_name_list.append(tweet["user"]['screen_name'])
            user_id_list.append("id_" + str(tweet["user"]['id']))

            rp_user_id = "id_" + str(tweet["in_reply_to_user_id"])
            rp_screen_name = tweet["in_reply_to_screen_name"]
            rp_status = "id_" + str(tweet["in_reply_to_status_id"]) if tweet["in_reply_to_status_id"] is not None else None

            t = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))
            datetime_list.append(t)

            text = tweet['text'] if "text" in tweet else tweet['full_text']

            rt_screen_name, rt_user_id,  rt_id, rt_type = None, None, None, None
            qt_id, qt_screen_name, qt_status = None, None, None

            mentions = set([x['screen_name'] for x in tweet['entities']['user_mentions']])

            if 'retweeted_status' in tweet: # It is a retweet
                text = tweet['retweeted_status']['text'] if 'text' in tweet['retweeted_status'] else tweet['retweeted_status']['full_text']
                try:
                    text = tweet['retweeted_status']['extended_tweet']['full_text']
                    mentions = set([x['screen_name'] for x in tweet['retweeted_status']['extended_tweet']['entities']['user_mentions']])
                except:
                    pass
                rt_screen_name = tweet['retweeted_status']['user']['screen_name']
                rt_user_id = "id_" + str(tweet['retweeted_status']['user']['id'])
                rt_id = "id_" + str(tweet['retweeted_status']['id'])
                rt_type = 'official'
                
            if 'quoted_status' in tweet: # In reply to tweet data
                qt_id = "id_" + str(tweet["quoted_status"]["user"]["id"])
                qt_screen_name = tweet["quoted_status"]["user"]["screen_name"]
                qt_status = tweet["quoted_status"]["text"] if 'text' in tweet['quoted_status'] else tweet['quoted_status']['full_text']
                try:
                    qt_status = tweet["quoted_status"]["extended_tweet"]['full_text']
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
                    rt_user_id = seed_tweets_dict[text][2]
            
            # Look for unnoficial uncredited retweets
            if rt_screen_name is None and text in seed_tweets_dict:
                rt_screen_name = seed_tweets_dict[text][0]
                rt_id = seed_tweets_dict[text][1]
                rt_user_id = seed_tweets_dict[text][2]
                rt_type = 'unofficial unaccredited'

            text_list.append(text)
            in_reply_to_status_id_list.append(rp_status)
            in_reply_to_user_id_list.append(rp_user_id)
            in_reply_to_screen_name_list.append(rp_screen_name)
            rt_screen_name_list.append(rt_screen_name)
            rt_user_id_list.append(rt_user_id)
            rt_id_list.append(rt_id)
            rt_type_list.append(rt_type)
            qt_id_list.append(qt_id)
            qt_screen_name_list.append(qt_screen_name)
            qt_status_list.append(qt_status)
            mentions_list.append(", ".join(list(mentions)))

            photo, video, gif = [], [], []
            if "media" in tweet['entities']:
                for media in tweet['extended_entities']['media']:
                    if media['type'] == 'photo':
                        photo.append(media['media_url'])
                    elif media['type'] == 'video':
                        video.append(media['video_info']['variants'][0]['url'])
                    elif media['type'] == 'animated_gif':
                        gif.append(media['video_info']['variants'][0]['url'])
            
            photos_list.append(", ".join(photo))
            videos_list.append(", ".join(video))
            gifs_list.append(", ".join(gif))

            if len(tweet['entities']['urls']) > 0:
                if "extended_tweet" in tweet:
                    url = [item['expanded_url'] for item in tweet['extended_tweet']['entities']['urls']]
                else:
                    url = [item['expanded_url'] for item in tweet['entities']['urls']]
                
                urls_list.append(", ".join(url))
                trunc_url_list.append(", ".join([re.search('://(www.)?([a-zA-Z0-9.-]+)',x).group(2) for x in url]))
                
            else:
                urls_list.append("")
                trunc_url_list.append("")

            if len(tweet['entities']['hashtags']) > 0  :
                hashtags_list.append(
                    ", ".join([item['text'] for item in tweet['entities']['hashtags']]))
            else:
                hashtags_list.append("")


    data = pd.DataFrame({
        "id" : id_list,
        "screen_name": screen_name_list,
        "user_id": user_id_list,
        "text": text_list,
        "rt_from_screen_name": rt_screen_name_list,
        "rt_from_user_id": rt_user_id_list,
        "rt_from_id": rt_id_list,
        "qt_from_screen_name": qt_screen_name_list,
        'qt_status': qt_status_list,
        "in_reply_to_screen_name": in_reply_to_screen_name_list,
        "in_reply_to_status_id": in_reply_to_status_id_list,
        "mentions": mentions_list,
        "datetime":datetime_list,
        "rt_type": rt_type_list,
        "url":urls_list,
        "trunc_url":trunc_url_list,
        "hashtags":hashtags_list,
        "photos":photos_list,
        "videos":videos_list,
        "gifs":gifs_list})

    return data

class process_tweets():
    def __init__(self, day_to_process):
        self.day_to_process = day_to_process

        print("> tidy stream")
        self.tweets = tidy_tweets('data/raw/stream_tweets_{}.json'.format(day_to_process))
        print(">> extract seed")
        self.extract_seed_tweets(get_media=True)
        
        print(">> extract retweets")
        self.extract_seed_retweets()
        
        print(">> get id values")
        tweets_ids = self.tweets.id.values
        del self.tweets
        
        print("> tidy rest")
        self.tweets = tidy_tweets('data/raw/rest_tweets_{}.json'.format(day_to_process))
        print(">> filtering tweets not in stream")
        self.tweets = self.tweets[~self.tweets.id.isin(tweets_ids)]
        print(">> extract seed")
        self.extract_seed_tweets(get_media=True)

        print(">> extact_retweets")
        self.extract_seed_retweets()
        del self.tweets

        self.unify_daily_followers_list()
        
    
        
    def extract_seed_tweets(self, get_media=False):
        '''
        Filters influencer tweets 
        input: raw json files
        output: 
            - seed_tweets.csv
            - seed_tweet_ids.csv (to track future retweets)
        '''
        print(">>> Extracting seed tweets df, saving to data/processed/seed_tweets/seed_tweets_<week>.csv")
        
        seed_tweets = self.tweets[(self.tweets.user_id.isin(user_ids))].drop_duplicates('id')

        self.len_new_tweets = len(seed_tweets)
        if get_media:
            print('getting media')
            for idx, row in seed_tweets.iterrows():

                if len(row['photos']) > 0:
                    for photo in row['photos'].split(", "):
                        try:
                            wget.download(photo, "data/processed/media_by_tweet/{}.jpg".format(row['id']))
                        except Exception as e:
                            pass

                if len(row['videos']) > 0:
                    for video in row['videos'].split(", "):
                        try:
                            wget.download(video, "data/processed/media_by_tweet/{}.mp4".format(row['id']))
                        except Exception as e:
                            pass

                if len(row['gifs']) > 0:
                    for gif in row['gifs'].split(", "):
                        try:
                            wget.download(gif, "data/processed/media_by_tweet/{}.mp4".format(row['id']))
                        except Exception as e:
                            pass

        # Write full dataframe
        if not os.path.isfile("data/processed/seed_tweets/seed_tweets_{}.csv".format(time.strftime("%y%W"))):
            seed_tweets.to_csv('data/processed/seed_tweets/seed_tweets_{}.csv'.format(time.strftime("%y%W")), index=False)
        else:
            seed_tweets.to_csv('data/processed/seed_tweets/seed_tweets_{}.csv'.format(time.strftime("%y%W")), index=False, header=False, mode='a')
        
        print(">>> Extracting seed tweets_id list, saving to data/seed_tweets_ids.csv")
        #  Keep a list of seed tweets ids
        with open('data/processed/seed_tweets_ids.csv', 'a') as f: 
            for tweet_id in seed_tweets.id.values:
                    f.write("%s\n" % tweet_id)
        
    def extract_seed_retweets(self):
        '''
        Extracts engagement with influencer tweets. Separates all from candace owens and charlie kirk
        for processing purposes. 

        input: all tidy tweets
        output: 
        - retweets.csv
        - retweets_cc.csv (candace owens and charlie kirk)
        '''
        print(">>> Extracting engagement from seeds df, saving to data/processed/engagement/engagement.csv")
        with open('data/processed/seed_tweets_ids.csv') as file:
            ids = file.read().splitlines()
        
        # Filtering out candace and charlie's retweets
        
        seed_retweets = self.tweets[ self.tweets.rt_from_screen_name.isin(screen_names_rest) | ### retweet
                                    (
                                        (self.tweets.rt_from_id.isna()) &
                                        (self.tweets.in_reply_to_screen_name.isin(screen_names_rest) &
                                        (self.tweets.in_reply_to_status_id.notna())))  | ### reply
                                    (
                                        (self.tweets.rt_from_id.isna()) &
                                        (self.tweets.qt_from_screen_name.isin(screen_names_rest))) ### quote
                                    ]
        
        print('finish filtering')
        if not os.path.isfile('data/processed/seed_retweets/retweets_from_seeds_{}.csv'.format(time.strftime("%y%W"))):
            seed_retweets.to_csv("data/processed/seed_retweets/retweets_from_seeds_{}.csv".format(time.strftime("%y%W")), index=False)
        else:
            seed_retweets.to_csv("data/processed/seed_retweets/retweets_from_seeds_{}.csv".format(time.strftime("%y%W")), index=False, header=False, mode='a')
        
        
        print(">>> Extracting retweeters screen_name and id, saving to data/retweeters_users.csv")
        if 'retweeters_users.csv' in os.listdir('data/processed/'):
            current_retweeters = pd.read_csv('data/processed/retweeters_users.csv')[["screen_name","user_id"]]
            new_retweeters = seed_retweets[~seed_retweets.user_id.isin(current_retweeters.user_id)][["screen_name","user_id"]]
            new_retweeters = new_retweeters.drop_duplicates()
        else:
            new_retweeters = seed_retweets[["screen_name","user_id"]].drop_duplicates()
        
        new_retweeters.to_csv('data/processed/retweeters_users.csv', index=False, mode='a')
        n_retweets = len(seed_retweets)
        n_rtters = len(new_retweeters)

        # Collecting candace and charlies retweets

        seed_retweets = self.tweets[ self.tweets.rt_from_screen_name.isin(screen_names_cc) | ### retweet
                                    (
                                        (self.tweets.rt_from_id.isna()) &
                                        (self.tweets.in_reply_to_screen_name.isin(screen_names_cc) &
                                        (self.tweets.in_reply_to_status_id.notna())))  | ### reply
                                    (
                                        (self.tweets.rt_from_id.isna()) &
                                        (self.tweets.qt_from_screen_name.isin(screen_names_cc))) ### quote
                                    ]


        if not os.path.isfile('data/processed/seed_retweets/retweets_from_seeds_cc_{}.csv'.format(time.strftime("%y%W"))):
            seed_retweets.to_csv("data/processed/seed_retweets/retweets_from_seeds_cc_{}.csv".format(time.strftime("%y%W")), index=False)
        else:
            seed_retweets.to_csv("data/processed/seed_retweets/retweets_from_seeds_cc_{}.csv".format(time.strftime("%y%W")), index=False, header=False, mode='a')


        print(">>> Extracting retweeters screen_name and id, saving to data/retweeters_users_cc.csv")
        if 'retweeters_users_cc.csv' in os.listdir('data/'):
            current_retweeters = pd.read_csv('data/processed/retweeters_users_cc.csv')[["screen_name","user_id"]]
            new_retweeters = seed_retweets[~seed_retweets.user_id.isin(current_retweeters.user_id)][["screen_name","user_id"]]
            new_retweeters = new_retweeters.drop_duplicates()
        else:
            new_retweeters = seed_retweets[["screen_name","user_id"]].drop_duplicates()

        new_retweeters.to_csv('data/processed/retweeters_users_cc.csv', index=False, mode='a')
        
        n_retweets_cc = len(seed_retweets)
        n_rtters_cc = len(new_retweeters)

        report = pd.DataFrame({"date":[self.day_to_process], "new_seed_tweets":[self.len_new_tweets], "n_retweet":[n_retweets],\
                "new_rtters":[n_rtters], "new_rtweets_cc":[n_retweets_cc], "new_rtters_cc":[n_rtters_cc]})
        if not os.path.isfile('process_report.csv'):
            report.to_csv("process_report.csv", index=False)
        else:
            report.to_csv("process_report.csv", index=False, header=False, mode='a')

    def unify_daily_followers_list(self):
        '''Takes all seed and retweeters followers files
        (different hours or access points) and creates a single dataframe
        to collect their profiles'''
        seed_files = os.listdir('data/processed/seed_followers')
        seed_files = [f for f in seed_files if 'seed_followers_{}'.format(self.day_to_process) in f]
        print(seed_files)
        all_files = []
        for file in seed_files:
            all_files.append(pd.read_csv('data/processed/seed_followers/{}'.format(file), header = None))

        daily_seed_followers = pd.concat(all_files)
        daily_seed_followers.columns = ['ego', 'follower']
        daily_seed_followers.drop_duplicates(['ego','follower'], inplace=True)
        daily_seed_followers.to_csv('data/processed/seed_followers/seed_daily_followers_{}.csv'.format(self.day_to_process), index=False)

        del daily_seed_followers
        del all_files

        retweeters_files = os.listdir('data/processed/retweeters_followers')
        retweeters_files = [f for f in retweeters_files if 'retweeters_followers_{}'.format(self.day_to_process) in f]
        print(retweeters_files)
        all_files = []
        for file in retweeters_files:
            print(file)
            try:
                all_files.append(pd.read_csv('data/processed/retweeters_followers/{}'.format(file), header = None))
            except Exception as e:
                print(e)

        try:
            daily_retweeters_followers = pd.concat(all_files[:8])
            daily_retweeters_followers.columns = ['ego', 'follower']
            daily_retweeters_followers.drop_duplicates(['ego','follower'], inplace=True)
            daily_retweeters_followers.to_csv('data/processed/retweeters_followers/retweeters_daily_followers_{}_0.csv'.format(self.day_to_process), index=False)
        except:
            pass
        try:
            daily_retweeters_followers = pd.concat(all_files[8:])
            daily_retweeters_followers.columns = ['ego', 'follower']
            daily_retweeters_followers.drop_duplicates(['ego','follower'], inplace=True)
            daily_retweeters_followers.to_csv('data/processed/retweeters_followers/retweeters_daily_followers_{}_1.csv'.format(self.day_to_process), index=False)
        except:
            pass

if __name__ == "__main__":
    ### Designed to be processed daily with a cron job

    users = pd.read_csv("data/seed_users.csv")
    user_ids = ["id_" + str(x) for x  in users.user_id.values]

    ### Separating candace owens and charlie kirk to manage engagement processing
    screen_names_cc = ['RealCandaceO','charliekirk11']
    screen_names_rest = [x for x in users.screen_name.values if x not in screen_names_cc]
    
    yesterday = dt.datetime.strftime(dt.datetime.now() - dt.timedelta(1), '%y%m%d')

    print("Processing day: ", yesterday)
    process_tweets(day_to_process=yesterday)

