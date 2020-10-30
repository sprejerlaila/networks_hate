# Disrupting networks of online hate

Hello! This repo contains the full code used for the data collection of the networks of hate project.

This includes: 

	- Continuous streaming of organic tweets for a list of seed users
	- Continuous streaming of retweets from these seed users
	- Collection of media contained in organic tweets
	- Collection of seed and retweeters followers
	- Collection of seed friends
	- Collection of seed and retweeters profiles
	(all these require crontab and access to Twitter API)
 
	- Toxicity analysis of organic tweets (Perspective API)
	- Bot analysis of retweeters (Botometer API)
	- Demographic inference of retweeters (M3 inference library)
	(all these are processed posteriorly)


	
    
