# Comunity Analyser

## How to setup?

1. Enable to use command "nkf".
2. Enable to use python module "requests_oauthlib".
   (Run "pip install requests_oauthlib")
2. Run "sh setup.sh".
   This script:
       a) downloads "http://www.lr.pi.titech.ac.jp/~takamura/pubs/pn_ja.dic",  
          (You can use "http://www.lr.pi.titech.ac.jp/~takamura/pubs/pn_en.dic" instead of it.  
           See "http://www.lr.pi.titech.ac.jp/~takamura/pndic_ja.html", or "http://www.lr.pi.titech.ac.jp/~takamura/pndic_en.html")  
       b) changes the encoding of "pn_ja.dic" to "UTF-8" with "LF" using "nkf",  
       c) puts "pn_ja.dic" to "settings", and  
       d) downloads "http://www.programming-magic.com/file/20080725011348/tiny_segmenter.py".  
3. If you don't have Twitter developer API, get it from "https://dev.twitter.com/".  
4. Edit "settings/user.ini" by your Twitter developer keys.  

Now, you can run Comunity Analyzer.

## How to use?

1. Run "python all.py".
