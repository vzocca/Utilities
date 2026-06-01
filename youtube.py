# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 15:51:11 2026

@author: vzocc
"""

import yt_dlp

# Inserisci qui il link YouTube
url = "https://www.youtube.com/watch?v=EjnM43IQYiQ"
#url = "https://www.dailymotion.com/video/x1d4u73"

ydl_opts = {
    'outtmpl': '%(title)s.%(ext)s',
    'format': 'bestvideo+bestaudio/best',
    'merge_output_format': 'mp4',
}

# with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#     ydl.download([url])
    
    
#url = "https://www.youtube.com/watch?v=VIDEO_ID"

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])