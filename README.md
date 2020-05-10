# Disrupting networks of online hate - Data collection

Files:
- **stream_seeds.py:** 
  
  input: seed_users.csv
  
	output: daily files saved to 'data/seed_tweets/seed_tweets_<date>.csv'
	
- **get_followers.py:** 

	input: seed_users.csv
  
  output: daily files saved to 'data/seed_folllowers/followers_<date>.csv'
	
- **process_tweets.py:** 

  input: date

	- tidy_tweets: converts raw tweets into dataframe
  
	- extract_seed_tweets: 
  
      output1: dataframe with seed_tweets
    
      output2: list with seed_tweets ids
  
  - extract_seed_retweets:
  
      input: seed_tweets id list
    
      output: dataframe with relevant retweets
    
