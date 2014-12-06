#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014, Masahiro Yano 
# Licensed under the BSD licenses. 
# https://github.com/masayano 
#
# What is this?
#
#   [tab separated tweets file: screen_name, user_id, tweet]
#   -> [tab separated word count file: word, count]
#
import sys
import json
import codecs
import re

s = re.compile('')
p = re.compile('^[a-zA-Z0-9_\-\+\*\/\\\:;@`<>"#\$%&\'()=~]+$')

def wordCount(counter, fileName):
    for line in codecs.open(fileName, 'r', 'utf-8'):
        text = re.sub(r'[,!\.\?\t\r\n\{\}\|\[\]]', ' ', line.split('\t')[-1])
        words = text.split()
        for word in words:
            if re.match(p, word):
                if counter.has_key(word):
                    counter[word] += 1
                else:
                    counter[word] = 1

if __name__=='__main__':
    counter = {}
    if len(sys.argv) >= 2:
        for fileName in sys.argv[1:]:
            print "[Word counting]", fileName
            wordCount(counter, fileName)
        fout = codecs.open(fileName+'.count', 'w', 'utf-8')
        for item in sorted(counter.items(), key=lambda x:x[1], reverse=True):
            fout.write(item[0] + '\t' + str(item[1]) + '\n')
        fout.close()
    else:
        print "Usage: python wordCounter.py [tweets file name(s)]"
