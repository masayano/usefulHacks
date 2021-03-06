#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014, Masahiro Yano 
# Licensed under the BSD licenses. 
# https://github.com/masayano 
#

import sys,os
import json
import codecs

ENCODE = 'utf-8'

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/modules')

from tiny_segmenter import TinySegmenter

ts = TinySegmenter()

def __escapeJSONContent(jsonContent):
    return jsonContent.replace('\n','\\n').replace('\t','\\t')

def __writeReplyDB(replyDBFile, replyDB):
    fout = codecs.open(replyDBFile, 'w', 'utf-8')
    json.dump(replyDB, fout, indent=2, ensure_ascii=False)
    fout.close()

def __writeUserDB(userDBFile, userDB):
    fout = codecs.open(userDBFile, 'w', 'utf-8')
    json.dump(userDB, fout, indent=2, ensure_ascii=False)
    fout.close()

def trimReplies(replyFile, replyDBFile, userDBFile):
    replyDB = {}
    userDB  = {}
    replies = json.loads(codecs.open(replyFile, 'r', ENCODE).read())
    for userId,replies_of_user in replies.items():
        userId = int(userId)
        userName = replies_of_user['userName']
        if not userDB.has_key(userId):
            userDB[userId] = []
        if not userName in userDB[userId]:
            userDB[userId].append(userName)
        for reply in replies_of_user['replies'].values():
            toUserId   = int(reply['toUserId'])
            toUserName = reply['toUserName']
            if not userDB.has_key(toUserId):
                userDB[toUserId] = []
            if not toUserName in userDB[toUserId]:
                userDB[toUserId].append(toUserName)
            if not replyDB.has_key(userId):
                replyDB[userId] = {}
            if not replyDB[userId].has_key(toUserId):
                replyDB[userId][toUserId] = []
            replyDB[userId][toUserId].append(":".join(ts.segment(__escapeJSONContent(reply['text']))))
    __writeReplyDB(replyDBFile, replyDB)
    __writeUserDB(userDBFile, userDB)

if __name__=='__main__':
    trimReplies('data/replies.json', 'data/replyDB.json', 'data/userDB.json')

