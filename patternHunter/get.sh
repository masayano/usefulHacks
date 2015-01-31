#!/bin/sh
while [ 1 -eq 1 ]
do
    sleep 5
    TEST=`ps auxw | grep "python script/getTweet.py" | grep -v "grep"`
    if [ -n "$TEST" ]; then
        echo `date`" : do \"python script/getTweet.py\""
        python script/getTweet.py
    fi
done
