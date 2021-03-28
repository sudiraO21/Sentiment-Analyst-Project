# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 01:59:41 2020

@author: tangg
"""
# Tangguh Sudira Oktafiandariento 
# tangguhsudirao@gmail.com

import tweepy
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import sqlite3


# Create SQL Table
conn = sqlite3.connect("tweet_data.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS tweet(
   tweetId INTEGER PRIMARY KEY AUTOINCREMENT,
   user TEXT,
   tanggal DATE,
   tweet TEXT,
   sentiment INTEGER);
""")
conn.commit()
cursor.close()

import os
from dotenv import load_dotenv

load_dotenv()
consumer_key = os.getenv('consumer_key')
consumer_secret = os.getenv('consumer_secret')
access_token = os.getenv('access_token')
access_token_secret = os.getenv('access_token_secret')

# Get & Update tweet
def update_data():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    search_words = 'vaksin covid'
    new_search = search_words + " -filter:retweets"
    tgl = datetime.date.today()
    twodays = datetime.timedelta(days=4)
    rangetgl = tgl - twodays
    tweets = tweepy.Cursor(api.search,
                        q=new_search,
                        lang="in",
                        tweet_mode='extended',
                        since=rangetgl).items(1000)

    items = []
    for tweet in tweets:
        item = []
        item.append(tweet.id)
        item.append(tweet.user.screen_name)
        item.append(tweet.created_at)
        item.append (' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet.full_text).split()))
        items.append(item)
    
    conn = sqlite3.connect("tweet_data.db")

    cursor = conn.cursor()

    crud_query = '''INSERT or IGNORE INTO tweet (tweetId, user, tanggal, tweet) values (?,?,?,?);'''

    for row in range(0,len(items)):
        input_list = items[row]
        cursor.execute(crud_query,input_list)
    
    conn.commit()
    cursor.close()
    
    print('Data telah diupdate\n')
    return

# Update sentiment 
def sentiment_analysis():
    
    conn = sqlite3.connect("tweet_data.db")
    cursor = conn.cursor()
    cursor.execute('SELECT tweetId ,tweet FROM tweet')
    
    pos_list= open("./kata_positif.txt","r")
    pos_kata = pos_list.readlines()
    neg_list= open("./kata_negatif.txt","r")
    neg_kata = neg_list.readlines()
    
    
    for row in cursor.fetchall():
        tweetId = row[0]
        tweet= (row[1],)
        
        for item in tweet:
            count_p = 0
            count_n = 0
            for kata_pos in pos_kata:
                if kata_pos.strip() in item:
                    count_p +=1
            for kata_neg in neg_kata:
                if kata_neg.strip() in item:
                    count_n +=1
            S = (count_p - count_n)
            Update = (S,tweetId)
            cursor.execute('''UPDATE tweet SET sentiment=? WHERE tweetId=?;''', Update )   
    
    conn.commit()
    cursor.close()
    
    print('Nilai sentiment telah diupdate\n')
    return
    
# Show Data
def show_data():
    date1 = input('tanggal awal (fomat: YYYY-MM-DD) :')   
    date2 = input('tanggal akhir (fomat: YYYY-MM-DD) :')
    
    conn = sqlite3.connect("tweet_data.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT user, tanggal, tweet FROM tweet
                   WHERE tanggal BETWEEN ? AND ?''',(date1,date2))
                  
    rev_df = pd.DataFrame(data=cursor.fetchall(), columns=['user','tanggal','tweet'])
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(rev_df)
    conn.commit()
    cursor.close()
    

def visualisasi():
    date1 = input('tanggal awal (fomat: YYYY-MM-DD) :')   
    date2 = input('tanggal akhir (fomat: YYYY-MM-DD) :')    
    
    conn = sqlite3.connect("tweet_data.db")

    cursor = conn.cursor()
    cursor.execute('''SELECT sentiment FROM tweet
                   WHERE tanggal BETWEEN ? AND ?''',(date1,date2))
    
    sent = cursor.fetchall()
    print ("Nilai rata-rata: "+str(np.mean(sent)))
    print ("Standar deviasi: "+str(np.std(sent)))
    print ("Median: "+str(np.median(sent)))
    
    labels, counts = np.unique(sent, return_counts=True)
    plt.bar(labels, counts, align='center')
    plt.gca().set_xticks(labels)
    plt.show()
    
    conn.commit()
    cursor.close()

    
# Main program

while True:
    print('Apa yang ingin anda lakukan?')
    print('\t 1. Update Data')
    print('\t 2. Update Nilai Sentiment')
    print('\t 3. Lihat Data')
    print('\t 4. Visualisasi')
    print('\t 5. Keluar')
    
    userinput = input('\t Input Anda :')
    
    if userinput == '1' :
        update_data()
    elif userinput == '2' :
        sentiment_analysis()    
    elif userinput == '3' :
        show_data()    
    elif userinput == '4' :
        visualisasi()    
    elif userinput == '5' :
        print('Terima kasih telah menggunakan script ini.')
        break
    else :
        print('Maaf input anda salah. Mohon input pilihan yang tersedia.')