#!/bin/sh
for file in tweets/*.log
do
    python script/wordCounter.py $file
done

if [ ! -e analysis ]; then
    mkdir analysis
fi
./bin/analyzeWord tweets/*.count
