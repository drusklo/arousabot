#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import os

#Variables
messageid = 1
message = 'This is my test message'
user = 'test'
command = '/test'

#Reading from the current path
path = __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

#Database location
db = sqlite3.connect(path+'/arousabot.db')
cursor = db.cursor()

def createDB():
    cursor.execute('CREATE TABLE "messages" ("messageid"	INTEGER NOT NULL,"message"	TEXT,"command"	INTEGER,"user"	TEXT NOT NULL,"date"	TEXT NOT NULL,PRIMARY KEY("messageid"))')
    

def writeId():
    cursor.execute('INSERT INTO messages(messageid, message, command, user, date) VALUES(?, ?, ?, ?, datetime())',(messageid, message, command, user, ))
    db.commit()

createDB()

writeId()