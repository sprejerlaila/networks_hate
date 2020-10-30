# Disrupting networks of online hate - Data collection

## Folder structure

```
project
|   stream_tweets.py
|   get_rest_tweets.py
|   get_followers.py
|   get_friends.py
|   get_profiles.py
|   process_tweets.py
|   get_botometer.py
│
└───data
│   │   seed_users.csv
│   │   retweeters_users.csv
│   │   seed_tweets_ids.csv
│   │
│   └───raw
│   │      stream_tweets_yymmdd.json
│   │      rest_tweets_yymmdd.json
│   │      ...
│   │   
│   └───processed
│   │   │     
│   │   └───seed_tweets
│   │   │       	seed_tweets_yyww.json
│   │   │       	...
│   │   │
│   │   └───seed_retweets
│   │   │       	seed_retweets_yyww.json
│   │   │       	...
│   │   │
│   │   └───seed_followers
│   │   │       	seed_followers_yymmdd.json
│   │   │       	...
│   │   │
│   │   └───seed_friends
│   │   │       	seed_friends_yymmdd.json
│   │   │       	...
│   │   │
│   │   └───retweeters_followers
│   │   │       	retweeters_followers_yymmdd.json
│   │   │		collected_followers_ids.csv
│   │   │		errors_followers_ids.csv
│   │   │       	...
│   │   │       	
│   │   └───media
│   │   	id_xxxxxxx.jpg
│   │   	id_xxxxxxx.mp4
│   │   	...
│   │
│   └───profiles
│   │		seed_profiles_yyww.json
│   │		retweeters_profiles_yyww.json
│   │		collected_retweeters_profiles.csv
│   │   	...
│   │
│   └───botometer
│   │		botometer.json
│   │		collected_botometer_ids.csv
│   │		error_botometer_ids.csv
│   │		nonexistent_botometer_ids.csv

```

## File details:
- **stream_tweets.py:** 
  
  input: seed_users.csv
  
	output: stream_tweets_yymmdd.json
	
- **get_rest_tweets.py:** 

	input: seed_users.csv	
  	
	output: rest_tweets_yymmdd.json
	
	- get_timeline():
	
		Rate limit: 200tw/req. 900 req in 15 min window. --> 86,400 requests a day
	
	- get_mentions():
	
		Rate limit: 200tw/req. 180 req in 15 min window. --> 17,280 requests a day

- **process_tweets.py:** 

  input: date (automatically loads stream and rest raw tweets)

	- tidy_tweets: converts raw tweets into dataframe
  
	- extract_seed_tweets: 
  
      output1: update seed_tweets.csv (dataframe with tweets from seed users)
    
      output2: update seed_tweets_ids.csv (list with seed_tweets ids)
  
  - extract_seed_retweets:
  
      input: seed_tweets_ids.csv
    
      output1: update retweets_from_seeds.csv (dataframe with relevant retweets)
      
      output2: update retweeters_users.csv (dataframe with screen_name and user_id from all retweeters)

	
- **get_followers.py:** 

	Rate limit: 5000/req. 15 req in 15 min window. --> max 7.2M followers or 1,440 users a day

	input: seed_users.csv; retweeters_users.csv
  
  output: \<seed|retweeters\>\_followers_yymmdd.csv
	
- **get_friends.py:** 

	Rate limit: 5000/req. 15 req in 15 min window. --> max 7.2M followers or 1,440 users a day

	input: seed_users.csv; retweeters_users.csv
  
  output: seed_friends_yymmdd.csv
  
- **get_profiles.py:** 

	Rate limit: 900 req in 15 min window. Runs offline --> max 86,400 users a day

	input: seed_users.csv; retweeters_users.csv
  
  output: update seed_profiles_yyww.json; retweeters_profiles_yyww.json
	
    
