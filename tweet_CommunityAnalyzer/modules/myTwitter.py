#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
from requests_oauthlib import OAuth1Session
import json
import time
import datetime
import codecs
from requests.exceptions import ConnectionError

def auth(configFile):
    inifile = ConfigParser.SafeConfigParser()
    inifile.read(configFile)
    CK = inifile.get('SYSTEM', 'ConsumerKey')
    CS = inifile.get('SYSTEM', 'ConsumerSecret')
    AT = inifile.get('SYSTEM', 'AccessToken')
    AS = inifile.get('SYSTEM', 'AccessTokenSecret')
    return OAuth1Session(CK, CS, AT, AS)

def __getTimestamp():
    d = datetime.datetime.today()
    return d.strftime("%Y-%m-%d %H:%M:%S")

def __getUserId(timeline):
    if len(timeline) > 0:
        return timeline[0]['user']['id']
    else:
        print "[ERROR]", __getTimestamp()
        print "        Please tweet at least once."
        return -1

def getId(twitter, userName):
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    prm = {'screen_name':userName}
    req = twitter.get(url, params = prm)
    if req.status_code == 200:
        timeline = json.loads(req.text)
        return __getUserId(timeline)
    else:
        print "[ERROR]", __getTimestamp()
        print "        Get tweets failed."
        print "        Error code:", req.status_code
        return -1

def getFollowIds(twitter, userId):
    url = "https://api.twitter.com/1.1/friends/ids.json"
    prm = {"user_id":userId}
    req = twitter.get(url, params = prm)
    if req.status_code == 200:
        ids = json.loads(req.text)
        return ids['ids']
    else:
        print "[ERROR]", __getTimestamp()
        print "        Get follows failed."
        print "        Error code:", req.status_code
        return []

def __trimReplies(\
            timeline,\
            searchId,\
            searchedIds,\
            replies):
    newUserIds = []
    searchId = int(searchId)
    for tweet in timeline:
        in_reply_to_user_id = tweet['in_reply_to_user_id']
        if in_reply_to_user_id != None:
            if  not in_reply_to_user_id in searchedIds\
            and not in_reply_to_user_id in newUserIds:
                newUserIds.append(in_reply_to_user_id)
            tweetId = int(tweet['id'])
            trimmedReply = {
                    'toUserId'  :in_reply_to_user_id,
                    'toUserName':tweet['in_reply_to_screen_name'],
                    'date'      :tweet['created_at'],
                    'text'      :tweet['text']}
            if replies.has_key(searchId):
                if not replies[searchId]['replies'].has_key(tweetId):
                        replies[searchId]['replies'][tweetId] = trimmedReply
            else:
                replies[searchId] = {'userName':tweet['user']['screen_name'],'replies':{}}
                replies[searchId]['replies'][tweetId] = trimmedReply
    return newUserIds

def __getReplies(\
        twitter,\
        searchId,\
        searchedIds,\
        replies):
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    prm = {"user_id":searchId, 'count':200}
    try:
        req = twitter.get(url, params = prm)
        if req.status_code == 200:
            timeline = json.loads(req.text)
            return __trimReplies(\
                    timeline,\
                    searchId,\
                    searchedIds,\
                    replies)
        elif req.status_code == 429:
            print "[INFO]", __getTimestamp()
            print "       API limit. 15 min sleep."
            time.sleep(15*60)
            return __getReplies(\
                    twitter,\
                    searchId,\
                    searchedIds,\
                    replies)
        else:
            print "[ERROR]", __getTimestamp()
            print "        Get tweets of", searchId, "failed."
            print "        Error code:", req.status_code
            return []
    except ConnectionError as e:
        d = datetime.datetime.today()
        print "[ERROR]", d.strftime("%Y-%m-%d %H:%M:%S")
        print "        Connection error occured."
        print "        UserId:", searchId
        print "        1 min sleep, and search again."
        return __getReplies(\
                twitter,\
                searchId,\
                searchedIds,\
                replies)

def __getRepliesRecursively(\
        twitter,\
        searchId,\
        searchedIds,\
        maxDepth,\
        currentDepth,\
        replies):
    if currentDepth < maxDepth:
        newUserIds = __getReplies(\
                twitter,\
                searchId,\
                searchedIds,\
                replies)
        for newUserId in newUserIds:
            __getRepliesRecursively(\
                    twitter,\
                    newUserId,\
                    searchedIds,\
                    maxDepth,\
                    currentDepth+1,\
                    replies)

def getRepliesRecursively(\
        twitter,\
        searchIds,\
        maxDepth,\
        replies,\
        repliesFile):
    currentDepth = 0
    searchedIds = []
    for i,searchId in enumerate(searchIds):
        print 'Progress:', i+1, '/', len(searchIds)
        __getRepliesRecursively(\
                twitter,\
                searchId,\
                searchedIds,\
                maxDepth,\
                currentDepth,\
                replies)
    fout = codecs.open(repliesFile, 'w', 'utf-8')
    json.dump(replies, fout, indent=2, ensure_ascii=False)
    fout.close()
