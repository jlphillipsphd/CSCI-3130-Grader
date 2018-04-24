#!/usr/bin/python

import sqlite3 as lite
import os

filelist = os.listdir(os.getcwd())
flag = False
if 'settings.sqlite3' not in filelist:
    flag = True
else:
    user_choice = input('Do you really want to drop database ? Type "yes" to continue\n ')
    if user_choice.isalpha() and user_choice == 'yes':
        flag = True

if not flag:
    exit(0)


con = lite.connect('settings.sqlite3')
with con:
    cur = con.cursor()
    cur.execute('DROP TABLE IF EXISTS PATHS')
    cur.execute("CREATE TABLE paths ( LOGISIM_HOME VARCHAR NOT NULL, GRADING_PATH VARCHAR NOT NULL, import_path  VARCHAR ); ")

