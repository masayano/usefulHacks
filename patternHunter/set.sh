#!/bin/sh
if [ ! -e bin ]; then
    mkdir bin
fi
g++ src/analyzeWord.cpp -std=c++11 -o bin/analyzeWord -O3
