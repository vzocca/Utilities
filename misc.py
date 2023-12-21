# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 07:27:31 2023

@author: vzocc
"""

#! usr/bin/python
from datetime import datetime
import os
import re

home = 'C:\\Users\\vzocc\\Documents\\Giornali\\'
    
def split_on_digits(s):
    return filter(None, re.split(r'(\d+)', s))

def clean_str(s):
    print(s)
    pattern = r'\[riviste\]\s*(.*)'
    match = re.search(pattern, s)

    if match:
        result = match.group(1)  # Get the part captured by the parentheses
        return result  # Output: 'Melaverde'
    else:
        return s
    
    

def date_folder_create():
    today = datetime.now()
    
    try:
        os.mkdir(home + today.strftime('%Y-%m-%d'))
    except (FileExistsError):
        os.mkdir(home + today.strftime('%Y-%m-%d') + '-bis')
    
pattern = r'( N\.\d+ | N\. \d+ |_\d+|\d+|-)'    
l = [re.split(pattern, f.split('-')[0])[0].strip() for f in os.listdir(home)]
l = [clean_str(f) for f in l]
l = [f.split(".pdf")[0] for f in l]

print(l)
print(set(l) )

