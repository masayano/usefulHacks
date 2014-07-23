#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014, Masahiro Yano 
# Licensed under the BSD licenses. 
# https://github.com/masayano 
#

import sys,os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/modules')

import myTwitter

def __loadReplies(repliesFile):
    if not os.path.exists(repliesFile):
        open(repliesFile, 'w').write('{}')
    return json.loads(open(repliesFile, 'r').read())

def gatherReplies(userName, twitterFile, repliesFile, depth):
    twitter = myTwitter.auth(twitterFile)
    replies = __loadReplies(repliesFile)
    targetId  = myTwitter.getId(twitter, userName)
    searchIds = myTwitter.getFollowIds(twitter, targetId)
    searchIds.append(targetId)
    myTwitter.getRepliesRecursively(\
            twitter,\
            searchIds,\
            depth,\
            replies,\
            repliesFile)

if __name__=="__main__":
    targetID = raw_input("Input target twitter ID > ")
    print 'Gather tweets started.'
    gatherReplies.gatherReplies(targetID, 'settings/user.ini', 'data/replies.json', 1)
