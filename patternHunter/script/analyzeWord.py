#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014, Masahiro Yano 
# Licensed under the BSD licenses. 
# https://github.com/masayano 
#
# What is this?
#
#   [tab separated word count file"s": word, count]
#   -> [tab separated word slope/average file:
#               word,
#               slope of smoothed probability / average,
#               JSON word number history (not smoothed),
#               JSON word smoothed probability history]
#
import os
import sys
import numpy as np
import json
from datetime import datetime as dt

MIN_AVERAGE_PROBABILITY = 0.000001

def loadFile(\
        smoothedNumMatrix,\
        smoothedProbMatrix,\
        wordCounters,\
        totalWordNums,\
        fileName):
    wordCounter  = {}
    totalWordNum = 0
    for line in open(fileName, 'r'):
        parts = line.split('\t')
        word  = parts[0]
        count = int(parts[1])
        wordCounter[word] = count
        if not smoothedNumMatrix.has_key(word):
            smoothedNumMatrix [word] = []
            smoothedProbMatrix[word] = []
        totalWordNum += 1
    wordCounters .append(wordCounter)
    totalWordNums.append(float(totalWordNum))

def makeMatrix(\
        smoothedNumMatrix,\
        smoothedProbMatrix,\
        wordCounters,\
        totalWordNums):
    wordTypeNum = float(len(smoothedNumMatrix.keys()))
    for i in range(len(wordCounters)):
        wordCounter  = wordCounters [i]
        totalWordNum = totalWordNums[i]
        totalNumAfterSmoothed = totalWordNum + wordTypeNum
        for key in smoothedNumMatrix.keys():
            if wordCounter.has_key(key):
                smoothedNumber = wordCounter[key] + 1 # smoothing
            else:
                smoothedNumber = 1 # smoothing
            probability = smoothedNumber / totalNumAfterSmoothed
            smoothedNumMatrix [key].append(smoothedNumber)
            smoothedProbMatrix[key].append(probability)

def calcPValue(smoothedProbMatrix):
    pValues = {}
    results = {}
    for key, values_y in smoothedProbMatrix.items():
        values_x = range(len(values_y))
        x = np.array(values_x)
        y = np.array(values_y)
        z = np.polyfit(x, y, 1)
        average = np.average(y)
        results[key] = z[0] / average
    return results

def getDate():
    tdatetime = dt.now()
    return tdatetime.strftime('%Y_%m_%d_%H_%M')

def writeResults(\
        results,\
        smoothedNumMatrix,\
        smoothedProbMatrix):
    f = open('analysis/'+getDate()+'.log', 'w')
    for key, slope in sorted(results.items(), key=lambda x:x[1], reverse=True):
        probArray = [float("%.3g"%smoothedProb) for smoothedProb in smoothedProbMatrix[key]]
        averageProb = sum(probArray)/len(probArray)
        if averageProb > MIN_AVERAGE_PROBABILITY:
            numArray  = [smoothedNum-1 for smoothedNum  in smoothedNumMatrix[key]]
            f.write(key + '\t' + str(round(slope,4)) + '\t' + str(numArray) + '\t' + str(probArray) + '\n')
    f.close()

if __name__=='__main__':
    if not os.path.exists("analysis"):
        os.mkdir("analysis")
    smoothedNumMatrix  = {}
    smoothedProbMatrix = {}
    wordCounters  = []
    totalWordNums = []
    if len(sys.argv) >= 2:
        for fileName in sys.argv[1:]:
            print "[Load for analyzing]", fileName
            loadFile(\
                    smoothedNumMatrix,\
                    smoothedProbMatrix,\
                    wordCounters,\
                    totalWordNums,\
                    fileName)
        makeMatrix(\
                smoothedNumMatrix,\
                smoothedProbMatrix,\
                wordCounters,\
                totalWordNums)
        results = calcPValue(smoothedProbMatrix)
        writeResults(\
                results,\
                smoothedNumMatrix,\
                smoothedProbMatrix)
    else:
        print "Usage: python analyzeWord.py [word count file name(s)]"
