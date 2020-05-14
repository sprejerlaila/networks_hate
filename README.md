# Disrupting networks of online hate - Data collection

Files:
- **stream_seeds.py:** 
  
  input: seed_users.csv
  
	output: stream_tweets_\<date\>.json
	
- **rest_tweets.py:**

	input: seed_users.csv	
  	
	output: rest_tweets_\<date\>.json
	
- **get_followers.py:** 

	Rate limit: 5000/req. 15 req in 15 min window. --> 7.2M a day

	input: seed_users.csv; retweeters_users.csv
  
  output: followers_\<user_id\>_\<date\>.csv
	
- **get_friends.py:** 

	Rate limit: 5000/req. 15 req in 15 min window. --> 7.2M a day

	input: seed_users.csv; retweeters_users.csv
  
  output: friends_\<user_id\>_\<date\>.csv
  
- **get_profiles.py:** 

	Rate limit: 900 req in 15 min window. Runs offline

	input: seed_users.csv; retweeters_users.csv
  
  output: update seed_profiles.json; retweeters_profiles.json
	
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
    
