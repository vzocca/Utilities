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
    

pattern = r'( N\.\d+ | N\. \d+ |_\d+|\d+|-| N\d+ | N \d+ )'

pattern1 = r'( N\.\d+)'
pattern2 = r'( N\. \d+)'
pattern3 = r'( N\.\d+)'
pattern4 = r'( N\. \d+)'
pattern5 = r'(_\d+)'
pattern6 = r'(\d+)'
pattern7 = r'(-)'

l = os.listdir(home)

#l = ["La Civiltà Cattolica N.4163 - 2 Dicembre 2023.pdf"]

l = [re.split(pattern1, f.split('-')[0])[0].strip() for f in l]
l = [re.split(pattern2, f.split('-')[0])[0].strip() for f in l]
l = [re.split(pattern3, f.split('-')[0])[0].strip() for f in l]
l = [re.split(pattern4, f.split('-')[0])[0].strip() for f in l]
l = [re.split(pattern5, f.split('-')[0])[0].strip() for f in l]
l = [re.split(pattern6, f.split('-')[0])[0].strip() for f in l]
l = [re.split(pattern7, f.split('-')[0])[0].strip() for f in l]

l = [clean_str(f) for f in l]
l = [f.split(".pdf")[0] for f in l]

print(l)
l = set(l)
print(set(l) )

len(l)

