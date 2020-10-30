#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 11:47:33 2020

@author: lsprejer
"""
import os

os.mkdir('data/raw')
os.mkdir('data/processed')

os.mkdir('data/processed/seed_tweets')
os.mkdir('data/processed/seed_retweets')
os.mkdir('data/processed/seed_friends')
os.mkdir('data/processed/seed_followers')
os.mkdir('data/processed/retweeters_followers')

os.mkdir('data/profiles')
os.mkdir('data/media')
os.mkdir('data/botometer')
