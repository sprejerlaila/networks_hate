# Disrupting networks of online hate - Data collection

Files:
- **stream_tweets.py:** 
  
  input: seed_users.csv
  
	output: stream_tweets_\<date\>.json
	
- **get_rest_tweets.py:** 

	input: seed_users.csv	
  	
	output: rest_tweets_\<date\>.json

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
  
  output: \<seed|retweeters\>_followers_\<date\>.csv
	
- **get_friends.py:** 

	Rate limit: 5000/req. 15 req in 15 min window. --> max 7.2M followers or 1,440 users a day

	input: seed_users.csv; retweeters_users.csv
  
  output: \<seed|retweeters\>_friends_\<date\>.csv
  
- **get_profiles.py:** 

	Rate limit: 900 req in 15 min window. Runs offline --> max 86,400 users a day

	input: seed_users.csv; retweeters_users.csv
  
  output: update seed_profiles.json; retweeters_profiles.json
	

    
