# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 07:27:31 2023

@author: vzocc
"""

#! usr/bin/python
from datetime import datetime
import os

today = datetime.now()

home = 'C:\\Users\\vzocc\\Documents\\Giornali\\'

try:
    os.mkdir(home + today.strftime('%Y-%m-%d'))
except (FileExistsError):
    os.mkdir(home + today.strftime('%Y-%m-%d') + '-bis')