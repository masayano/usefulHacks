#!/bin/sh
while [ 1 -eq 1 ]
do
    sleep 5
    TEST=`ps auxw | grep "python script/getTweet.py" | grep -v "grep" | wc -l`
    if [ $TEST = 0 ]; then
        echo `date`" : do \"python script/getTweet.py\""
        python script/getTweet.py
    fi
done
