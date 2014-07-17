#!/bin/bash

cd `dirname $0`

python parent.py ini/parent.ini data/parent.activity
python child.py  ini/child1.ini data/child1.reply data/child1.task data/child1.log
python child.py  ini/child2.ini data/child2.reply data/child2.task data/child2.log
python child.py  ini/child3.ini data/child3.reply data/child3.task data/child3.log
