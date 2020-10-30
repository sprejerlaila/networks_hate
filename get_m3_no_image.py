#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 12:07:41 2020

@author: lailasprejer
"""

from m3inference import M3Inference, get_lang
import pickle
import os
import sys
import json

def prepare_profiles_for_m3(file, n_file):
    ''' Input: raw profile files 
        Output: 
            - drop duplicated ids in each file
            - drop profiles with errors when collected
            - adds Lang variable if none (needed for m3 inference) 
    '''
    
    collected_profiles = set()
    with open('../data/profiles/raw/{}'.format(file)) as json_data:
        profiles = json_data.readlines()

    for pr in profiles:
        try:
            prof = json.loads(pr)
        except:
            print(pr)
            continue
        
        if 'errors' in prof or prof['id'] in collected_profiles:
            continue
        
        collected_profiles.add(prof['id'])        
        prof['lang'] = get_lang(prof['id_str'])
        
        with open('../data/profiles/processed/profiles_{}.json'.format(n_file), 'a') as tf:
            json.dump(prof, tf)
            tf.write('\n')

def get_m3_no_image(file, n_file):  
    '''
    Get demographics using m3 inference library. Save to json file
    Input: clean profiles 
    Output: pickle file with demographics dict. Keys are ids
    '''
    
    m3 = M3Inference(use_full_model=False) # Because we don't have the profile images
    pred = m3.infer('../data/profiles/processed/{}'.format(file))
    
    # For simplicity save to pickle because output is a dict
    pickle.dump(pred, open( "processed/m3_no_image{}.p".format(n_file), "wb"))

if __name__ == "__main__":
    files = os.listdir('../data/profiles/raw')
    files = [x for x in files if "profiles" in x]
    
    if sys.argv[1] == 'all': 
        print("files to process: ", files)
        
        for n_file, file in enumerate(files):
            # Prepare raw profiles
            prepare_profiles_for_m3(file = files[n_file], n_file = n_file)
        
            # Get m3 to json file
            get_m3_no_image(file = files[n_file], n_file = n_file)
    else:
        n_file = int(sys.argv[1])
        print("processing file: ", file[n_file])	
        
        # Prepare raw profiles
        prepare_profiles_for_m3(file = files[n_file], n_file = n_file)
    
        # Get m3 to json file
        get_m3_no_image(file = files[n_file], n_file = n_file)
    
