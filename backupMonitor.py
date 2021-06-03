#!/usr/bin/python
# -*- coding: utf-8 -*-

# Any new command needs to be declared in the command list and added to the tinydic array

import os
import subprocess
import time
import datetime
from datetime import datetime
import sys
import requests
import json
import configparser
import getpass


#Getting username
user = getpass.getuser()

#Reading from the current path
path = __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

#Define your config, db and log file here
config_file = path+'/arousabot.conf'


#Parsing config file
config = configparser.ConfigParser()
config.read(config_file)
apiKey = config['DEFAULT']['ApiKey']
botchat = int(config['CHATS']['botchat'])
myid = int(config['USERS']['myid'])
alexid = int(config['USERS']['alexid'])
faid = int(config['USERS']['faid'])

#Backup Monitor function
def backupMon():
    # Check the last time folder was modified
    command = "stat -c %y /mnt/data/backup | cut -c1-10"
    proc = subprocess.Popen(command,stdout=subprocess.PIPE,shell=True)
    (out1, err) = proc.communicate()
    # Encode as utf-8 to remobe the b' at the begining and \n at the end 
    out1decoded = out1.decode('utf-8')
    # Remove the extra line
    outwithoutline = out1decoded.rstrip('\n')
    # Convert backup time to datetime format
    global backupDay
    backupDay = datetime.strptime(outwithoutline, '%Y-%m-%d')
    #print('Backup Day: ', backupDay)
    # Check the current day and format it to be only dd/mm/yyyy
    global currentDay
    currentDay = datetime.now().strftime('%Y-%m-%d')
    # Convert current day to datetime format
    currentDay = datetime.strptime(currentDay,'%Y-%m-%d')
    #print('Current Day: ', currentDay)
    # Check current time
    global currentTime
    currentTime = datetime.now().strftime('%H:%M:%S')
    #currentTime = datetime.strptime(currentTime,'%H:%M:%S')
    #print('Current Time: ', currentTime)

while True:
   
    #Backup function
    backupMon()

    #POST MESSAGES only to my user or users in the whitelist
    bot_chat="https://api.telegram.org/bot"+str(apiKey)+"/sendMessage?chat_id="+str(myid)+"&text="

    #Backup Monitor
    if backupDay < currentDay and currentTime > '14:30:00':
        backupMessage = 'Backup has failed!'
        print(backupMessage)
        requests.post(bot_chat+backupMessage)
    else:
        print('Backup is completed or has not run yet')

    time.sleep(60)
    break