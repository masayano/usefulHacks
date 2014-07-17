#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014, Masahiro Yano 
# Licensed under the BSD licenses. 
# https://github.com/masayano 
#

import ConfigParser

def loadConfig(CONFIG_FILE):
    inifile = ConfigParser.SafeConfigParser()
    inifile.read(CONFIG_FILE)
    CK = inifile.get('SYSTEM', 'ConsumerKey')
    CS = inifile.get('SYSTEM', 'ConsumerSecret')
    AT = inifile.get('SYSTEM', 'AccessToken')
    AS = inifile.get('SYSTEM', 'AccessTokenSecret')
    return [CK, CS, AT, AS]
