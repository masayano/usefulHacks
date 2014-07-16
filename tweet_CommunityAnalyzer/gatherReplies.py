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
    args = sys.argv
    if len(args) == 2:
        gatherReplies(args[1], 'settings/user.ini', 'data/replies.json', 1)
    else:
        print "Usage: python gatherReplies.py [target user ID]"
