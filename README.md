# Disrupting networks of online hate - Data collection

Files:
- **stream_seeds.py:** 
  
  input: seed_users.csv
  
	output: daily json files saved to 'data/seed_tweets/seed_tweets_<date>.json'
	
- **rest_tweets.py:**

	input: seed_users.csv	
  	
	output: json files saved to 'data/seed_tweets/rest_tweets_<date>.json'
	
- **get_followers.py:** 

	Rate limit: 5000/req. 15 req in 15 min window. --> 7.2M a day

	input: seed_users.csv
  
  output: daily files saved to 'data/seed_folllowers/followers_<date>.csv'
	
- **process_tweets.py:** 

  input: date (automatically loads stream and rest raw tweets)

	- tidy_tweets: converts raw tweets into dataframe
  
	- extract_seed_tweets: 
  
      output1: dataframe with seed_tweets
    
      output2: list with seed_tweets ids
  
  - extract_seed_retweets:
  
      input: seed_tweets id list
    
      output: dataframe with relevant retweets
    
