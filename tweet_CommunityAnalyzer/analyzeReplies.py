#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014, Masahiro Yano 
# Licensed under the BSD licenses. 
# https://github.com/masayano 
#

import json
import codecs

ENCODE = 'utf-8'

def __loadDictionary(dictionaryFile):
    dictionary = {}
    lines = codecs.open(dictionaryFile, 'r', ENCODE).read().split('\n')
    for line in lines:
        tokens = line.split(':')
        if len(tokens) == 4:
            dictionary[tokens[0]] = float(tokens[3])
    return dictionary

def __calcReplyEmotionScore(dictionary, reply):
    totalScore = 0;
    tokens = reply.split(':')
    for word,score in dictionary.items():
        count = 0;
        for token in tokens:
            if token == word:
                count += 1
        totalScore += count*(score+1)
    return totalScore;

def __calcRepliesEmotionScore(dictionary, replies):
    score = 0;
    for reply in replies:
        score += __calcReplyEmotionScore(dictionary, reply);
    return int(score);

def __writeAnalysis(analysis, analysisFile):
    fout = codecs.open(analysisFile, 'w', ENCODE)
    for analysis_of_user in sorted(analysis):
        for toUserNameJSON,talk in sorted(analysis_of_user.items(), key=lambda x: x[1][2]):
            json.dump(talk[0], fout, ensure_ascii=False)
            fout.write('\t')
            fout.write(toUserNameJSON+'\t')
            json.dump(talk[1], fout, ensure_ascii=False)
            fout.write('\t')
            json.dump(talk[2], fout, ensure_ascii=False)
            fout.write('\t')
            json.dump(talk[3], fout, ensure_ascii=False)
            fout.write('\n')

def analyzeReplies(replyDBFile, userDBFile, dictionaryFile):
    replyDB    = json.loads(codecs.open(replyDBFile, 'r', ENCODE).read())
    userDB     = json.loads(codecs.open(userDBFile,  'r', ENCODE).read())
    dictionary = __loadDictionary(dictionaryFile)
    analysis = []
    progress = 1;
    for userId,replies_of_user in replyDB.items():
        print "Progress:", progress, "/", len(replyDB)
        progress += 1
        userNames = userDB[userId]
        analysis_of_user = {}
        for toUserId,replies in replies_of_user.items():
            toUserNames = userDB[toUserId]
            score = __calcRepliesEmotionScore(dictionary, replies);
            analysis_of_user[json.dumps(toUserNames)] = [
                    userNames,
                    len(replies),
                    score,
                    replies]
        analysis.append(analysis_of_user)
    __writeAnalysis(analysis, 'data/analysis.tsv')

if __name__=='__main__':
    analyzeReplies('data/replyDB.json', 'data/userDB.json', 'settings/pn_ja.dic.utf8.lf')

