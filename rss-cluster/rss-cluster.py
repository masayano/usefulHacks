#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014, Masahiro Yano 
# Licensed under the BSD licenses. 
# https://github.com/masayano 
#
# What is this?
#
#   [RSS url list in 'rss_url.dat'] -> [contents clusterd by word frequency]
#
# IMPORTANT:
#
#  0:This script is written in "python 2.7".
#
#  1:This script uses "TinySegmenyer" to support Japanese.
#    See also http://www.programming-magic.com/20080726203844/
#
#  2:This script uses "bayon 0.1.1".
#    See also https://code.google.com/p/bayon/
#
import codecs
import sys
import os
import os.path
import platform
import datetime
import ConfigParser
import feedparser
from tiny_segmenter import TinySegmenter
import subprocess
import textwrap

ENCODE = 'utf-8'
if hasattr(sys,'setdefaultencoding'):
    sys.setdefaultencoding(ENCODE)

if getattr(sys, 'frozen', False):
    APP_PATH = os.path.dirname(sys.executable)
elif __file__:
    APP_PATH = os.path.dirname(__file__)

OS_NAME = platform.system()
if OS_NAME == 'Windows':
    RETURN = '\r\n'
else:
    RETURN = '\n'

TIMESTAMP = datetime.datetime.today().strftime('%Y%m%d-%H%M%S')
RESULT_FOLDER = os.path.join(APP_PATH, 'result')
RSS_URL_FILE = os.path.join(APP_PATH, 'rss_url.dat')
ERRLOG_FILE  = os.path.join(RESULT_FOLDER, TIMESTAMP + '-error.log')
FEATURE_FILE = os.path.join(RESULT_FOLDER, TIMESTAMP + '-feature.tsv')
CLUSTER_FILE = os.path.join(RESULT_FOLDER, TIMESTAMP + '-cluster.tsv')
CENTER_FILE  = os.path.join(RESULT_FOLDER, TIMESTAMP + '-center.tsv')
CONFIG_FILE  = os.path.join(APP_PATH, 'config.ini')
FEATURE_TITLE = 'title'
FEATURE_VEC   = 'vec'

if not os.path.exists(RESULT_FOLDER):
    os.mkdir(RESULT_FOLDER)
ferr = codecs.open(ERRLOG_FILE, 'w', ENCODE)

class SYSTEM:
    WRAP_LENGTH = 100
class RSS:
    CHANNEL_NAME = 'title'
    ITEM_NAME    = 'title'
    ITEM_DATE    = 'updated'
    ITEM_MAIN    = 'description'
    ITEM_OTHERS  = ['author']
class CLUSTERING:
    CLUSTER_NUM = 10
    FLAG_IDF    = True

S = SYSTEM()
R = RSS()
C = CLUSTERING()

def init():
    inifile = ConfigParser.SafeConfigParser()
    inifile.read(CONFIG_FILE)
    global S, R, C
    S.WRAP_LENGTH = int(inifile.get('SYSTEM', 'WRAP_LENGTH'))
    R.CHANNEL_NAME = inifile.get('RSS', 'CHANNEL_NAME')
    R.ITEM_DATE    = inifile.get('RSS', 'ITEM_DATE')
    R.ITEM_NAME    = inifile.get('RSS', 'ITEM_NAME')
    R.ITEM_MAIN    = inifile.get('RSS', 'ITEM_MAIN')
    R.ITEM_OTHERS  = inifile.get('RSS', 'ITEM_OTHERS').split('+')
    C.CLUSTER_NUM =  inifile.get('CLUSTERING', 'CLUSTER_NUM')
    C.FLAG_IDF    = (inifile.get('CLUSTERING', 'FLAG_IDF') == 'True')

def getRSSFeeds():
    feeds = []
    for line in open(RSS_URL_FILE, 'r'):
        url = line.rstrip()
        print "[URL]", url
        feeds.append(feedparser.parse(url))
    return feeds

def getPapers(feeds):
    properties  = [R.ITEM_DATE, R.ITEM_NAME, R.ITEM_MAIN]
    papers = {}
    error  = []
    errorCount = 0
    for feed in feeds:
        channel = feed['feed']
        if channel.has_key(R.CHANNEL_NAME):
            channelName = channel[R.CHANNEL_NAME].replace('\n', ' ').replace('\t', ' ')
        else:
            channelName = 'Channel name not found.'
            ferr.write('[no title feed]' + str(channel.keys()) + '\n')
        for item in feed['entries']:
            title   = ''
            content = {}
            flag    = True
            for p in properties + R.ITEM_OTHERS:
                if item.has_key(p):
                    value = item[p].replace('\n', ' ').replace('\t', ' ')
                    if p == R.ITEM_NAME:
                        title = value
                    else:
                        content[p] = value
                else:
                    errorCount += 1
                    flag = False
            content[R.CHANNEL_NAME] = channelName
            if flag:
                papers[title] = content
            else:
                error.append(title)
    for e in error:
        ferr.write('[error] \"' + e + '\" was discarded.\n')
    print '->', str(len(papers.keys())), ' items are assigned.'
    print '->', errorCount, ' items are discarded (broken data).'
    return papers

def deleteOddChars(text):
    chars = ['!', '\"', '#', '$',  '%', \
             '&', '\'', '(', ')',  '*', \
             '+', ',',  '-', '.',  '/', \
             '@', ':',  ';', '<',  '=', \
             '>', '?',  '[', '\\', ']', \
             '^', '_',  '{', '|',  '}', '~']
    for char in chars:
        text = text.replace(char, ' ')
    text = text.split(' ')
    while text.count('') > 0:
        text.remove('')
    text = ' '.join(text)
    return text

def featureExtraction(papers):
    features = []
    for title in papers.keys():
        feature = {FEATURE_TITLE:title, FEATURE_VEC:{}}
        content = papers[title]
        words = extractWords(deleteOddChars(title + ' ' + content[R.ITEM_MAIN]))
        for word in words:
            word = word.replace(' ', '')
            if feature.has_key(word):
                feature[FEATURE_VEC][word] += 1
            else:
                feature[FEATURE_VEC][word] = 1
        features.append(feature)
    return features    

def extractWords(inStr):
    ts = TinySegmenter()
    return ts.segment(inStr)

def writeFeatureData(features):
    fout = codecs.open(FEATURE_FILE, 'w', ENCODE)
    for feature in features:
        fout.write(feature[FEATURE_TITLE] + '\t')
        vec = feature[FEATURE_VEC]
        tmp = []
        for key in vec.keys():
            tmp.append(key + '\t' + str(vec[key]))
        fout.write('\t'.join(tmp) + '\n')

def makeCommand4bayon():
    command = ''
    if OS_NAME == 'Windows':
        command += os.path.join(APP_PATH, 'bayon.exe ')
    else:
        command += 'bayon '
    if C.FLAG_IDF:
        command += '--idf'
    command += (' -n ' + C.CLUSTER_NUM)
    command += (' -c ' + CENTER_FILE)
    command += (' '    + FEATURE_FILE + ' > ' + CLUSTER_FILE)
    return command

def writeCluters(papers):
    clusters = codecs.open(CLUSTER_FILE, 'r', ENCODE).readlines()
    for i, line in enumerate(clusters):
         fileName  = RESULT_FOLDER + '/' + TIMESTAMP + '-[' + str(i + 1) + '].result'
         fout      = codecs.open(fileName, 'w', ENCODE)
         titles    = line.rstrip().split('\t')
         paperList = []
         for j, title in enumerate(titles):
             if j > 0:
                 content = papers[title]
                 paper  = '[' + R.ITEM_DATE + '] ' + content[R.ITEM_DATE] + '\n'
                 paper += '[' + R.ITEM_NAME + ']\n'
                 paper += '\n'.join(textwrap.wrap(title, S.WRAP_LENGTH)) + '\n'
                 for prop in [R.ITEM_MAIN, R.CHANNEL_NAME] + R.ITEM_OTHERS:
                     paper += '[' + prop + ']\n'
                     paper += '\n'.join(textwrap.wrap(content[prop], S.WRAP_LENGTH)) + '\n'
                 paper += '\n'
                 paperList.append(paper)
         for p in sorted(paperList, reverse=True):
             fout.write(p)

if __name__ == "__main__":
    print 'Initialization',
    init()
    print '...finished.'

    print 'Download xml'
    feeds = getRSSFeeds()
    print '...finished.'

    print 'Creating data of papers'
    papers = getPapers(feeds)
    print '...finished.'

    print 'Feature extraction',
    features = featureExtraction(papers)
    print '...finished.'
 
    print 'Write the feature',
    writeFeatureData(features)
    print '...finished.'

    print 'Clustering by \"bayon 0.1.1\":'
    command = makeCommand4bayon()
    print '[command] ', command
    subprocess.call(command, shell=True)
    print '...finished.'

    print 'Write clusters',
    writeCluters(papers)
    print '...finished.'
