#!/bin/bash
#
# Copyright 2014, Masahiro Yano 
# Licensed under the BSD licenses. 
# https://github.com/masayano 
#

echo "[INFO] Downloading \"pn_ja.duc\" from \"http://www.lr.pi.titech.ac.jp/~takamura/pubs/pn_ja.dic\"."
wget http://www.lr.pi.titech.ac.jp/~takamura/pubs/pn_ja.dic

echo "[INFO] Setting the encoding of \"pn_ja.dic\" to UTF-8/LF."
nkf -w -Lu pn_ja.dic > settings/pn_ja.dic.utf8.lf
rm pn_ja.dic

echo "[INFO] Downloading \"TinySegmenter for python\" from \"http://www.programming-magic.com/file/20080725011348/tiny_segmenter.py\"."
wget http://www.programming-magic.com/file/20080725011348/tiny_segmenter.py
mv tiny_segmenter.py modules
