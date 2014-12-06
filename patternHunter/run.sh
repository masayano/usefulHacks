for file in tweets/*.log
do
    python script/wordCounter.py $file
done
python script/analyzeWord.py tweets/*.count
