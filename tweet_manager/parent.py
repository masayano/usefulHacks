#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014, Masahiro Yano 
# Licensed under the BSD licenses. 
# https://github.com/masayano 
#

import sys
import os
import common
from requests_oauthlib import OAuth1Session
import json
import codecs

ENCODE = 'utf-8'
CONFIG_FILE   = 'ini/parent.ini'
ACTIVITY_FILE = 'data/parent.activity'

def loadArgs():
    if len(sys.argv) == 3:
        global CONFIG_FILE, ACTIVITY_FILE
        CONFIG_FILE   = sys.argv[1]
        ACTIVITY_FILE = sys.argv[2]
        if not os.path.exists(ACTIVITY_FILE):
            open(ACTIVITY_FILE, 'w').write('')
    else:
        print 'Usage:',\
              'python parent.py',\
              '<Config file path>',\
              '<Activity file path>'
        sys.exit()

def init():
    loadArgs()
    [CK, CS, AT, AS] = common.loadConfig(CONFIG_FILE)
    return OAuth1Session(CK, CS, AT, AS)

def getTimeline(twitter):
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    params = {}
    req = twitter.get(url, params = params)
    if req.status_code == 200:
        return json.loads(req.text)
    else:
        print "[ERROR] Get tweets failed."
        print "        Error code:", req.status_code
        return []

def getFavs():
    url = 'https://api.twitter.com/1.1/favorites/list.json'
    params = {'count': 200}
    req = twitter.get(url, params = params)
    if req.status_code == 200:
        return json.loads(req.text)
    else:
        print "[ERROR] Get favorites failed."
        print "        Error code:", req.status_code
        return []

def addNewTimeline(timeline, activities):
    for tweet in timeline[::-1]:
        tweetText = tweet['text'].replace('\n', '\\n')
        if tweet['retweeted']:
            text = ('RTid: ' + str(tweet['retweeted_status']['id']) + '\t' + tweetText)
        else:
            text = tweetText
        if not text in activities:
            activities.insert(0, text)
    return activities

def addNewFavs(favs, activities):
    for fav in favs[::-1]:
        tweetText = fav['text'].replace('\n', '\\n')
        text = ('FavId: ' + str(fav['id']) + '\t' + tweetText)
        if not text in activities:
            activities.insert(0, text)
    return activities

def refreshActivities(timeline, favs):
    activities = codecs.open(ACTIVITY_FILE, 'r', ENCODE).read().split('\n')
    addNewTimeline(timeline, activities)
    addNewFavs    (favs,     activities)
    codecs.open(ACTIVITY_FILE, 'w', ENCODE).write('\n'.join(activities))

if __name__ == '__main__':
    print 'Initializing:',
    twitter  = init()
    print 'finished.'

    print 'Loading user timeline:'
    timeline = getTimeline(twitter)
    print 'finished.'

    print 'Loading user favorites:'
    favs = getFavs()
    print 'finished.'

    print 'Refreshing activities:'
    refreshActivities(timeline, favs)
    print 'finished.'

