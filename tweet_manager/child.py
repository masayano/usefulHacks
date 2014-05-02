#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import ConfigParser
import common
from requests_oauthlib import OAuth1Session
import json
import codecs

ENCODE = 'utf-8'

CONFIG_FILE = 'ini/child.ini'
REPLY_FILE  = 'data/child.reply'
TASK_FILE   = 'data/child.task'
LOG_FILE    = 'data/child.log'
REMOVE_UNFOLLOWBACKED = False
FOLLOW_BACK           = False

def loadArgs():
    if len(sys.argv) == 5:
        global CONFIG_FILE, REPLY_FILE, TASK_FILE, LOG_FILE
        CONFIG_FILE = sys.argv[1]
        REPLY_FILE  = sys.argv[2]
        TASK_FILE   = sys.argv[3]
        LOG_FILE    = sys.argv[4]
        if not os.path.exists(REPLY_FILE):
            open(REPLY_FILE,      'w').write('')
        if not os.path.exists(TASK_FILE):
            open(TASK_FILE, 'w').write('')
        if not os.path.exists(LOG_FILE):
            open(LOG_FILE,        'w').write('')
    else:
        print 'Usage:',\
              'python child.py',\
              '<Config file path>',\
              '<Reply file name>',\
              '<Task file path>',\
              '<Log file path>'
        sys.exit()

def loadFollowBackFlag():
    inifile = ConfigParser.SafeConfigParser()
    inifile.read(CONFIG_FILE)
    global FOLLOW_BACK, REMOVE_UNFOLLOWBACKED
    REMOVE_UNFOLLOWBACKED = (inifile.get('SETTING', 'RemoveUnfollowbacked') == 'True')
    FOLLOW_BACK           = (inifile.get('SETTING', 'FollowBack') == 'True')

def init():
    loadArgs()
    loadFollowBackFlag()
    [CK, CS, AT, AS] = common.loadConfig(CONFIG_FILE)
    twitter = OAuth1Session(CK, CS, AT, AS)
    return [twitter, []]

def loadTasks():
    tasks = codecs.open(TASK_FILE, 'r', ENCODE).read().split('\n')
    while (True):
        try:
            tasks.remove(u'')
        except:
            break
    return tasks

def doTask(twitter, task):
    if task.startswith('RTid: '):
        RTid = task.split('\t')[0][6:]
        url = "https://api.twitter.com/1.1/statuses/retweet/" + RTid + ".json"
        req = twitter.post(url)
    elif task.startswith('FavId: '):
        FavId = task.split('\t')[0][7:]
        params = {'id': FavId}
        url = "https://api.twitter.com/1.1/favorites/create.json"
        req = twitter.post(url, params = params)
    else:
        params = {'status': task.replace('\\n', '\n')}
        url = "https://api.twitter.com/1.1/statuses/update.json"
        req = twitter.post(url, params = params)
    if req.status_code == 200:
        return True
    else:
        print '[ERROR] Failed task:', task.replace('\\n', '\n')
        print '        Status_code:', req.status_code
        return False

def refreshTasks(tasks):
    codecs.open(TASK_FILE, 'w', ENCODE).write('\n'.join(tasks))

def manageTasks(twitter, logger):
    print 'Loading tweet tasks:'
    tasks = loadTasks()
    if len(tasks) == 0:
        print 'No tweet task was found.'
    else:
        print 'finished.'
        print 'Do task:'
        task = tasks[-1]
        if doTask(twitter, task):
            print 'finished.'
            print 'Refreshing tasks:'
            refreshTasks(tasks[:-1])
            print 'finished.'
            logger.append('[Done task] ' + task)

def getAllPages(twitter, url):
    output = []
    cursor = -1
    while True:
        params = {'cursor': cursor, 'count': 5000}
        req = twitter.get(url, params = params)
        if req.status_code == 200:
            newOutpus = json.loads(req.text)
            output.extend(newOutpus['ids'])
            cursor = newOutpus['next_cursor']
            if cursor == 0:
                return [True, output]
        else:
            return [False, req.status_code]

def getFriends(twitter):
    url = 'https://api.twitter.com/1.1/friends/ids.json'
    [getResult, result2] = getAllPages(twitter, url)
    if getResult:
        return result2
    else:
        print "[ERROR] Get friends failed."
        print "        Error code:", result2
        return []

def getFollowers(twitter):
    url = 'https://api.twitter.com/1.1/followers/ids.json'
    [getResult, result2] = getAllPages(twitter, url)
    if getResult:
        return result2
    else:
        print "[ERROR] Get followers failed."
        print "        Error code:", result2
        return []

def getScreenName(twitter, userId):
    url = 'https://api.twitter.com/1.1/users/show.json'
    params = {'user_id': userId}
    req = twitter.get(url, params = params)
    if req.status_code == 200:
        return json.loads(req.text)['screen_name']
    else:
        print '[ERROR] Failed to get screen_name of user_id:', userId
        return ''

def remove(twitter, userId, logger):
    url = 'https://api.twitter.com/1.1/friendships/destroy.json'
    params = {'user_id': userId}
    req = twitter.post(url, params = params)
    if req.status_code == 200:
        return True
    else:
        return False

def removeFF(twitter, friends, followers, logger):
    removeLogs = []
    for userId in friends:
        if not userId in followers:
            screen_name = getScreenName(twitter, userId)
            if screen_name != '' and remove(twitter, userId, logger):
                logger.append('[Remove] ' + screen_name)
            else:
                print ('[ERROR] Failed to remove \"' + screen_name + '\"')
    return removeLogs

def follow(twitter, userId, logger):
    url = 'https://api.twitter.com/1.1/friendships/create.json'
    params = {'user_id': userId, 'follow': 'true'}
    req = twitter.post(url, params = params)
    if req.status_code == 200:
        return True
    else:
        return False

def followFF(twitter, friends, followers, logger):
    followLogs = []
    for userId in followers:
        if not userId in friends:
            screen_name = getScreenName(twitter, userId)
            if screen_name != '' and follow(twitter, userId, logger):
                logger.append('[Follow] ' + screen_name)
            else:
                print '[ERROR] Failed to follow \"', screen_name, '\"'
    return followLogs

def manageFF(twitter, logger):
    print 'Getting friends:'
    friends = getFriends(twitter)
    print 'finished.'
    print 'Getting followers:'
    followers = getFollowers(twitter)
    print 'finished.'
    if REMOVE_UNFOLLOWBACKED:
        print 'Remove follow but not followed:'
        removeFF(twitter, friends, followers, logger)
        print 'finished.'
    if FOLLOW_BACK:
        print 'Follow followed but not follow:'
        followFF(twitter, friends, followers, logger)
        print 'finished.'

def getReplies(twitter):
    url = 'https://api.twitter.com/1.1/statuses/mentions_timeline.json'
    params = {}
    req = twitter.get(url, params = params)
    if req.status_code == 200:
        replies = []
        for reply in json.loads(req.text)[::-1]:
            text = reply['user']['screen_name']+':\t'+reply['text'].replace('\n', '\\n')
            replies.append(text)
        return replies
    else:
        print "[ERROR] Get replies failed."
        print "        Error code:", req.status_code
        return []

def refreshReplies(replies, logger):
    temp = codecs.open(REPLY_FILE, 'r', ENCODE).read().split('\n')
    for reply in replies:
        if not reply in temp:
            temp.insert(0, reply)
            logger.append('[Add reply] ' + reply)
    codecs.open(REPLY_FILE, 'w', ENCODE).write('\n'.join(temp))

def manageReplies(twitter, logger):
    print 'Getting replies:'
    replies = getReplies(twitter)
    print 'finished.'
    print 'Refreshing reply file:'
    refreshReplies(replies, logger)
    print 'finished.'

def refreshLogs(logger):
    logs = codecs.open(LOG_FILE, 'r', ENCODE).read().split('\n')
    for log in logger:
        logs.insert(0, log)
    codecs.open(LOG_FILE, 'w', ENCODE).write('\n'.join(logs))

if __name__ == '__main__':
    print 'Initializing:'
    [twitter, logger] = init()
    print 'finished.'

    manageTasks  (twitter, logger)
    manageFF     (twitter, logger)
    manageReplies(twitter, logger)

    print 'Refreshing logs:'
    refreshLogs(logger)
    print 'finished.'
