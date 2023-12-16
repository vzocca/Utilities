# -*- coding: utf-8 -*-
"""
Created on Sat Dec 16 14:29:59 2023

@author: vzocc
"""

import os
from os import walk
path='C:\\Users\\vzocc\\Documents\\GitHub'
#path='C:\\Users\\vzocc\\Projects\\Python'
keywords=['pysimplegui']

for root, dirs, files in walk(path):
    for name in files:      
        try:
            with open(os.path.join(root, name),'r') as f:
                data=f.read()
                data=data.lower()
                
                if keywords[0] in data:
                    print(root+'\''+name)

        except:
            pass