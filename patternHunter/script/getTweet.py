#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014, Masahiro Yano 
# Licensed under the BSD licenses. 
# https://github.com/masayano 
#
# What is this?
#
#   [Twitter public stream API 'sample.json']
#   -> [tab separated tweets file: screen_name, user_id, tweet]
#
import os
import ConfigParser
from requests_oauthlib import OAuth1Session
import json
from datetime import datetime as dt
import codecs

URL = 'https://stream.twitter.com/1.1/statuses/sample.json'

ENCODE = 'utf-8'

def loadConfig(configFile):
    inifile = ConfigParser.SafeConfigParser()
    inifile.read(configFile)
    CK = inifile.get('TWITTER', 'CK')
    CS = inifile.get('TWITTER', 'CS')
    AT = inifile.get('TWITTER', 'AT')
    AS = inifile.get('TWITTER', 'AS')
    return [CK, CS, AT, AS]

def getPublicStream(twitter):
    r = twitter.get(URL, stream=True)
    for line in r.iter_lines():
        if line:
            item = json.loads(line)
            processItem(item)

def getDate():
    tdatetime = dt.now()
    return tdatetime.strftime('%Y_%m_%d')

def processItem(item):
    if item.has_key('text') and item['user']['lang'] == 'en':
        userId   = str(item['user']['id'])
        userName = item['user']['screen_name']
        text     = item['text'].replace('\r',' ').replace('\n', ' ')
        myStr = userName + '\t' + userId + '\t' + text
        f = codecs.open("tweets/"+getDate()+".log", "a", ENCODE)
        f.write(myStr + '\n')
        f.close()

if __name__=='__main__':
    if not os.path.exists("tweets"):
        os.mkdir("tweets")
    [CK, CS, AT, AS] = loadConfig('twitter.ini')
    twitter = OAuth1Session(CK, CS, AT, AS)
    getPublicStream(twitter)
