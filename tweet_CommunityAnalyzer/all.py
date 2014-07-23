#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014, Masahiro Yano 
# Licensed under the BSD licenses. 
# https://github.com/masayano 
#

import gatherReplies
import trimReplies
import analyzeReplies

repliesFile = 'data/replies.json'
replyDBFile = 'data/replyDB.json'
userDBFile  = 'data/userDB.json'

if __name__=="__main__":
    targetID = raw_input("Input target twitter ID > ")
    print 'Gather tweets started.'
    gatherReplies.gatherReplies(targetID, 'settings/user.ini', repliesFile, 1)
    print 'Trimming tweets.'
    trimReplies.trimReplies(repliesFile, replyDBFile, userDBFile)
    print 'Analyzing replies.'
    analyzeReplies.analyzeReplies(replyDBFile, userDBFile, 'settings/pn_ja.dic.utf8.lf')
