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
import sqlite3
import argparse
from os.path import exists

verbose = 'false'

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument('-env', '--environment', help='Specify your environment')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose mode')
args = parser.parse_args()
if args.environment == 'PROD':
    print('This is PROD')
    env = ''
    if args.verbose:
        print('Verbose mode is enabled')
        verbose = 'true'
    else:
        print('Verbose mode is off')
elif args.environment == 'DEV':
    print('This is DEV')
    env = '_dev'
    if args.verbose:
        print('Verbose mode is enabled')
        verbose = 'true'
    else:
        print('Verbose mode is off')


# Getting hostname
host = os.uname()[1]

# Getting username
user = getpass.getuser()

# Reading from the current path
path = __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Define your config, db and log file here.
config_file = path+'/arousabot.conf'
pathTolog = path+'/arousabot.log'

# Check if config file exists
if exists(path+'/arousabot.conf'):
    print('Config File Exists')
else:
    print('Config file not available, it needs to be created for the application to run')
    quit()

# Check if log exists, if not, create it
if exists(path+'/arousabot.log'):
    print('Log File Exists')
else:
    print('Cannot find the log file, creating a new one...')
    logFile = open(pathTolog,'x')
    logFile.close()


# Initial DB set up
def setupdb():
    messageid = 1
    message = 'This is my test message'
    user = 'test'
    command = '/test'
    db = sqlite3.connect(path+'/arousabot'+env+'.db')
    cursor = db.cursor()
    cursor.execute('CREATE TABLE "messages" ("messageid"	INTEGER NOT NULL,"message"	TEXT,"command"	INTEGER,"user"	TEXT NOT NULL,"date"	TEXT NOT NULL,PRIMARY KEY("messageid"))')
    cursor.execute('INSERT INTO messages(messageid, message, command, user, date) VALUES(?, ?, ?, ?, datetime())',(messageid, message, command, user, ))
    db.commit()

# Check if the DB exists
if exists(path+'/arousabot'+env+'.db'):
    print('DB Exists')
else:
    print('DB not available, creating...')
    setupdb()

# Database location
db = sqlite3.connect(path+'/arousabot'+env+'.db')
cursor = db.cursor()

# Parsing config file
config = configparser.ConfigParser()
config.read(config_file)
apiKey = config['DEFAULT']['ApiKey'+env]
botchat = int(config['CHATS']['botchat'])
myid = int(config['USERS']['myid'])
alexid = int(config['USERS']['alexid'])
faid = int(config['USERS']['faid'])
btcholdings = float(config['CRYPTO']['btcholdings'])
ethholdings = float(config['CRYPTO']['ethholdings'])


# Whitelist
whitelist=[myid,faid,alexid]

# Command List
ip = "/ip"
temp = "/temp"
mycrypto = "/crypto"
mybtc = "/btc"
myeth = "/eth"
help = "/help"
hitchhiker1 = "What's the meaning of life?"
hitchhiker2 = "What is the meaning of life?"
pcup = "/pcup"

# If a command is not added here it will show as an error
tinydict = {ip,mycrypto,mybtc,myeth,temp,help,hitchhiker1,hitchhiker2,pcup}

# GET JSON DATA from Telegram API
receive_data="https://api.telegram.org/bot"+str(apiKey)+"/GetUpdates?offset=-1&limit=1"

# Variables for the Crypto Function
currentprice = 'https://www.bitstamp.net/api/v2/ticker/'


# Send function
def send():
    requests.post(bot_chat+message)

# Crypto functions
def crypto(coin='btc'):
    global operation
    new_request = requests.get(currentprice+coin+'eur')
    json_data = new_request.json()
    price = float(json_data['last'])
    global message
    if coin == 'btc':
        #print('BTC')
        operation = btcholdings * price
        operation = int(operation)
        message = 'This is the value of your '+coin+' holdings: \n'+str(operation)+' €'
    elif coin == 'eth':
        #print('ETH')
        operation = ethholdings * price
        operation = int(operation)
        message = 'This is the value of your '+coin+' holdings: \n'+str(operation)+' €'
        #requests.post(bot_chat+message)
    else:
        print('Failure')

# All my holdings
def holdings():
    global message
    crypto('btc')
    mybtc = operation
    crypto('eth')
    myeth = operation
    taxesBtc = int((mybtc - (19 / 100) * mybtc))
    taxesEth = int((myeth - (19 / 100) * myeth))
    afterTaxes = taxesBtc + taxesEth
    all = mybtc + myeth
    message = 'This is the value of all your holdings:\n BTC: '+str(mybtc)+' € \n BTC After Tax: '+str(taxesBtc)+' € \n ETH: '+str(myeth)+' € \n ETH After Tax: '+str(taxesEth)+' € \n TOTAL: '+str(all)+' € \n After Tax: '+str(afterTaxes)+' €'

# Logging function
def writeLog():
    logFile = open(pathTolog,'a')
    logFile.write(str(text))
    logFile.write(os.linesep)
    logFile.write(str(log_time))
    logFile.write(os.linesep)
    logFile.write(str(json_data))
    logFile.write(os.linesep)
    logFile.close()

# Read from Sqlite DB
def getId():
    global lastid
    cursor.execute('SELECT messageid FROM messages order by date desc limit 1')
    lastid = cursor.fetchone()

# Write Sqlite DB
def writeId():
    print(message_id)
    cursor.execute('INSERT INTO messages(messageid, message, command, user, date) VALUES(?, ?, ?, ?, datetime())',(message_id, message, text, username, ))
    db.commit()


while True:
    
    try:
        new_request = requests.get(receive_data)
        json_data = new_request.json()
    except requests.ConnectionError:
        pass

    editedMsgId = None
    message_id = None
    username = 'dummy'
    text = None
    chatType = None
    message = 'no message'
    userid = None
    #chatid = None

    #Misc Variables
    log_time = datetime.now()
    
# Reading JSON Data
    # This deals with normal messages in group chats
    if 'message' in json_data['result'][0] and json_data['result'][0]['message']['chat']['type'] == 'group':
        print('This is anything in a group')
        if 'text' in json_data['result'][0]['message'] and 'username' in json_data['result'][0]['message']['from']:
            print('This is a message')
            text = json_data['result'][0]['message']['text'] # This gets the message
            message_id = json_data['result'][0]['message']['message_id'] # This gets the message_id to avoid re-sending data
            userid = json_data['result'][0]['message']['from']['id'] # This gets the user_id
            username = json_data['result'][0]['message']['from']['username'] # This gets the username
            first_name = json_data['result'][0]['message']['from']['first_name'] # This gets the first_name
            chatid = json_data['result'][0]['message']['chat']['id'] # This gets the chat_id
            chatName = json_data['result'][0]['message']['chat']['title'] # This gets the chat Name
            chatType = json_data['result'][0]['message']['chat']['type'] # This gets the type of chat
        # This is in case the user doesn't have a username
        elif 'text' in json_data['result'][0]['message']:
            print('This is a message')
            text = json_data['result'][0]['message']['text'] # This gets the message
            message_id = json_data['result'][0]['message']['message_id'] # This gets the message_id to avoid re-sending data
            userid = json_data['result'][0]['message']['from']['id'] # This gets the user_id
            first_name = json_data['result'][0]['message']['from']['first_name'] # This gets the first_name
            chatid = json_data['result'][0]['message']['chat']['id'] # This gets the chat_id
            chatName = json_data['result'][0]['message']['chat']['title'] # This gets the chat Name
            chatType = json_data['result'][0]['message']['chat']['type'] # This gets the type of chat
        elif 'new_chat_participant' in json_data['result'][0]['message']:
            print('Ignoring this')
            message_id = json_data['result'][0]['message']['message_id'] # This gets the message_id to avoid re-sending data
            userid = json_data['result'][0]['message']['from']['id'] # This gets the user_id
            chatid = json_data['result'][0]['message']['chat']['id'] # This gets the chat_id
            username = json_data['result'][0]['message']['from']['username']
        elif 'left_chat_participant' in json_data['result'][0]['message']:
            print('Ignoring this')
            message_id = json_data['result'][0]['message']['message_id'] # This gets the message_id to avoid re-sending data
            userid = json_data['result'][0]['message']['from']['id'] # This gets the user_id
            chatid = json_data['result'][0]['message']['chat']['id'] # This gets the chat_id
            username = json_data['result'][0]['message']['from']['username']
    
        elif 'old_chat_member' in json_data['result'][0]['my_chat_member']:
            print('Ignoring this')
            userid = json_data['result'][0]['my_chat_member']['from']['id'] # This gets the user_id
            chatid = json_data['result'][0]['my_chat_member']['chat']['id'] # This gets the chat_id
            username = json_data['result'][0]['my_chat_member']['from']['username']

    # This deals with edited messages in group chats
    elif 'edited_message' in json_data['result'][0] and json_data['result'][0]['edited_message']['chat']['type'] == 'group':
        print('This is anything edited in a group')
        if 'text' in json_data['result'][0]['edited_message']:
            print('This is an edited message')
            editedMsg = json_data['result'][0]['edited_message']['text'] # This gets the edited message text 
            editedMsgId = json_data['result'][0]['edited_message']['message_id'] # This gets the edited message ID
            editedMsgdate = json_data['result'][0]['edited_message']['edit_date'] # This gets the edited message date
            date = json_data['result'][0]['edited_message']['date'] # This gets the original message date
            chatType = json_data['result'][0]['message']['chat']['type'] # This gets the type of chat

    
    # This deals with normal messages in private chats
    elif 'message' in json_data['result'][0] and json_data['result'][0]['message']['chat']['type'] == 'private':
        print('This is anything in a private chat')
        if 'text' in json_data['result'][0]['message'] and 'username' in json_data['result'][0]['message']['from']:
            print('This is a message')
            text = json_data['result'][0]['message']['text'] # This gets the message
            message_id = json_data['result'][0]['message']['message_id'] # This gets the message_id to avoid re-sending data
            userid = json_data['result'][0]['message']['from']['id'] # This gets the user_id
            username = json_data['result'][0]['message']['from']['username'] # This gets the username
            first_name = json_data['result'][0]['message']['from']['first_name'] # This gets the first_name
            chatid = json_data['result'][0]['message']['chat']['id'] # This gets the chat_id
            chatType = json_data['result'][0]['message']['chat']['type'] # This gets the type of chat
        elif 'text' in json_data['result'][0]['message']:
            print('This is a message')
            text = json_data['result'][0]['message']['text'] # This gets the message
            message_id = json_data['result'][0]['message']['message_id'] # This gets the message_id to avoid re-sending data
            userid = json_data['result'][0]['message']['from']['id'] # This gets the user_id
            first_name = json_data['result'][0]['message']['from']['first_name'] # This gets the first_name
            chatid = json_data['result'][0]['message']['chat']['id'] # This gets the chat_id
            chatType = json_data['result'][0]['message']['chat']['type'] # This gets the type of chat


    # This deals with edited messages in private chats
    elif 'edited_message' in json_data['result'][0] and json_data['result'][0]['edited_message']['chat']['type'] == 'private':
        print('This is anything edited in a private chat')
        if 'text' in json_data['result'][0]['edited_message']:
            print('This is an edited message')
            editedMsg = json_data['result'][0]['edited_message']['text'] # This gets the edited message text 
            editedMsgId = json_data['result'][0]['edited_message']['message_id'] # This gets the edited message ID
            editedMsgdate = json_data['result'][0]['edited_message']['edit_date'] # This gets the edited message date
            date = json_data['result'][0]['edited_message']['date'] # This gets the original message date
            chatid = json_data['result'][0]['edited_message']['chat']['id'] # This gets the chat_id
            chatType = json_data['result'][0]['edited_message']['chat']['type'] # This gets the type of chat


    # Read from SQLITE DB
    getId()

    # POST MESSAGES only to my user or users in the whitelist
    bot_chat="https://api.telegram.org/bot"+str(apiKey)+"/sendMessage?chat_id="+str(userid)+"&text="

    # POST Messages to everyone else
    bot_error="https://api.telegram.org/bot"+str(apiKey)+"/sendMessage?chat_id="+str(chatid)+"&text="


    # Checking if message has been sent
    if int((lastid)[0]) == message_id:
        print("Checking SQLITE DB, Message has already been sent")
        time.sleep(2)
    
    # Sending Messages 
        
    # Successful messages

    # Is my PC Up
    if text == pcup and int((lastid)[0]) != message_id and userid in whitelist and chatid == botchat:
        ping = os.system('ping -c 3 192.168.42.5')
        if ping == 0:
            message = 'Your computer is up'
        else:
            message = 'Your computer seems to be down'
        send()
        writeLog()

    # Requesting a IP
    if text == ip and int((lastid)[0]) != message_id and userid in whitelist and chatid == botchat:
        get_ip = requests.get('https://ipinfo.io/ip')
        message = 'This is your ip: '+get_ip.text.strip('\n')
        send()
        writeLog()

    #print(host)

    # Requesting temperature
    if text == temp and host == 'raspberrypi' and int((lastid)[0]) != message_id and userid in whitelist and chatid == botchat:
        from gpiozero import CPUTemperature
        cpu = CPUTemperature()
        message = 'CPU Temperature is: ' + str(cpu.temperature) + 'C'
        send()
        writeLog()

    # Requesting all holdings
    if text == mycrypto and int((lastid)[0]) != message_id and userid in whitelist and chatid == botchat:
        holdings()
        send()
        writeLog()

    # Requesting bitcoin
    if text == mybtc and int((lastid)[0]) != message_id and userid in whitelist and chatid == botchat:
        crypto('btc')
        send()
        writeLog()
    
    # Requesting ethereum
    if text == myeth and int((lastid)[0]) != message_id and userid in whitelist and chatid == botchat:
        crypto('eth')
        send()
        writeLog()
    
    # Error temperature
    if text == temp and host != 'raspberrypi' and int((lastid)[0]) != message_id and userid in whitelist and chatid == botchat:
        message = "Unable to provide the requested information"
        send()
        writeLog()

    # Help Command
    if text == help and int((lastid)[0]) != message_id and userid in whitelist and chatid == botchat:
        message = "I need somebody"
        send()
        writeLog()

    # Easter Egg
    if (text == hitchhiker1 or text == hitchhiker2) and int((lastid)[0]) != message_id:
        message = "42"
        send()
        writeLog()

    # Errors
    # Command Not Found
    if text not in tinydict and int((lastid)[0]) != message_id and userid in whitelist and chatid == botchat:
        message = "Command not found"
        send()
        writeLog()

    # Someone has added you to a group
    if text not in tinydict and int((lastid)[0]) != message_id and chatType == 'group':
        message = "Someone has added you to a group"
        send()
        writeLog()

    # Someone has removed you to a group
    if text not in tinydict and int((lastid)[0]) != message_id and chatType == 'group' and 'left_chat_participant' in json_data['result'][0]['message']:
        message = "Someone has removed you from a group"
        send()
        writeLog()

    # User not allowed
    if int((lastid)[0]) != message_id and userid not in whitelist:
        message = "Trespassers will be shot, survivors will be shot again"
        send()
        writeLog()

    # Write to SQlite DB and close connection
    if message_id != int((lastid)[0]):
        print(lastid)
        writeId()
        print('Adding record to DB')
    else:
        print('Record already exists')

    if verbose == "true":
        #print(json_data)
        print(text)
        print(log_time)
        print("This is the message that we are getting from the API: "+str(message_id))
        print("This is the last line that was written to the DB: "+str(lastid[0]))
        print('UserId: '+str(userid))
        #print (json.dumps(json_data,ensure_ascii=False,indent=2))

    time.sleep(2)
    break
