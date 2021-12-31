#!/usr/bin/python
# -*- coding: utf-8 -*-

##DEV##

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
# Enable this in order to get Raspberry Pi Temp
#from gpiozero import CPUTemperature
#if os.system("uname -a | grep raspberry") == True:
#else:
#    pass



#Getting hostname
host = os.uname()[1]

#Getting username
user = getpass.getuser()


#Reading from the current path
path = __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

#Define your config, db and log file here
config_file = path+'/arousabot.conf'
#pathTodb = path+'/dbId.db'
pathTolog = path+'/arousabot.log'

#Database location
db = sqlite3.connect(path+'/arousabot_dev.db')
cursor = db.cursor()

#Parsing config file
config = configparser.ConfigParser()
config.read(config_file)
apiKey = config['DEFAULT']['ApiKey']
apiKey_dev = config['DEFAULT']['ApiKey_DEV']
botchat = int(config['CHATS']['botchat'])
myid = int(config['USERS']['myid'])
alexid = int(config['USERS']['alexid'])
faid = int(config['USERS']['faid'])
btcholdings = float(config['CRYPTO']['btcholdings'])
ethholdings = float(config['CRYPTO']['ethholdings'])


#Whitelist
whitelist=[myid,faid,alexid]

#Command List
ip = "/ip"
temp = "/temp"
all = "/all"
mycrypto = "/crypto"
mybtc = "/btc"
myeth = "/eth"
help = "/help"
hitchhiker1 = "What's the meaning of life?"
hitchhiker2 = "What is the meaning of life?"
pcup = "/pcup"

# If a command is not added here it will show as an error
tinydict = {ip,mycrypto,mybtc,myeth,temp,help,hitchhiker1,hitchhiker2,pcup}

#Getting IP
#get_ip = requests.get('https://ipinfo.io/ip')


#GET JSON DATA from Telegram API - DEV
receive_data="https://api.telegram.org/bot"+str(apiKey_dev)+"/GetUpdates?offset=-1&limit=1"


#Messages
#ip_message = 'This is your ip: '+get_ip.text.strip('\n')

help_message = "I need somebody"

hitchhiker_message = "42"

error_message = "IP hasn't changed or the command is incorrect"

error_message2 = "Command not found"

error_message3 = "Trespassers will be shot, survivors will be shot again"

error_message4 = "Unable to provide the requested information"

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
    all = mybtc + myeth
    #message = 'This is the value of all your holdings: '+str(all)+' €'
    message = 'This is the value of all your holdings:\n BTC: '+str(mybtc)+' € \n ETH: '+str(myeth)+' € \n TOTAL: '+str(all)+' €'

#Logging function
def writeLog():
    logFile = open(pathTolog,'a')
    logFile.write(str(text))
    logFile.write(os.linesep)
    logFile.write(str(log_time))
    logFile.write(os.linesep)
    logFile.write(str(json_data))
    logFile.write(os.linesep)
    logFile.close()


#Read DB function
def readDbFile():
    global pathTodb
    pathTodb = ''
    global dbFile
    dbFile = open(pathTodb,'r')
    global readlastline
    readlastline = dbFile.readline()
    dbFile.close()

#Write DB function
def writeDbFile():
    dbFile = open(pathTodb,'w')
    dbFile.write(str(message_id))
    dbFile.close()

#SQLITE FUNCTIONS

#Read from Sqlite DB
def getId():
    global lastid
    cursor.execute('SELECT messageid FROM messages order by date desc limit 1')
    lastid = cursor.fetchone()
    #print(int(lastid[0]))

#Write Sqlite DB
def writeId():
    cursor.execute('INSERT INTO messages(messageid, message, command, user, date) VALUES(?, ?, ?, ?, datetime())',(message_id, message, text, username, ))
    db.commit()


#Enable Logging
#logging = 'false'

#Enable verbose mode
verbose = 'true'


while True:
    
    try:
        new_request = requests.get(receive_data) 
        json_data = new_request.json()
    except requests.ConnectionError:
        pass

    #Misc Variables
    log_time = datetime.now()
    
#Reading JSON Data
    try:
        text = json_data['result'][0]['message']['text'] # This gets the message
        message_id = json_data['result'][0]['message']['message_id'] # This gets the message_id to avoid re-sending data
        userid = json_data['result'][0]['message']['from']['id'] # This gets the user_id
        username = json_data['result'][0]['message']['from']['username'] # This gets the username
        chatid = json_data['result'][0]['message']['chat']['id'] # This gets the chat_id
    except KeyError: #This deals with the exceptions
        print(datetime.now())
        print("An Exception has ocurred, will keep going")
        pass

    #Read DB File
    #readDbFile()

    # Read from SQLITE DB
    getId()

    #POST MESSAGES only to my user or users in the whitelist - DEV
    bot_chat="https://api.telegram.org/bot"+str(apiKey_dev)+"/sendMessage?chat_id="+str(userid)+"&text="

    #POST Messages to everyone else - DEV
    bot_error="https://api.telegram.org/bot"+str(apiKey_dev)+"/sendMessage?chat_id="+str(chatid)+"&text="


    #Checking if message has been sent
    if int((lastid)[0]) == message_id:
        print("Checking SQLITE DB, Message has already been sent")
        time.sleep(2)
    #Sending Messages 
        
    #Successful messages

    #Is my PC Up
    if text == pcup and int((lastid)[0]) != message_id and userid in whitelist and chatid == botchat:
        ping = os.system('ping -c 3 192.168.42.5')
        if ping == 0:
            ping_message = 'Your computer is up'
        else:
            ping_message = 'Your computer seems to be down'
        message = ping_message
        requests.post(bot_chat+ping_message)
        writeLog()

    #Requesting a IP
    if text == ip and int((lastid)[0]) != message_id and userid in whitelist and chatid == botchat:
        #requests.post(bot_chat+ip_message)
        get_ip = requests.get('https://ipinfo.io/ip')
        ip_message = 'This is your ip: '+get_ip.text.strip('\n')
        message = ip_message
        requests.post(bot_chat+ip_message)
        writeLog()

    #print(host)

    #Requesting temperature
    if text == temp and host == 'raspberrypi' and int((lastid)[0]) != message_id and userid in whitelist and chatid == botchat:
        cpu = CPUTemperature()
        temp_message = 'CPU Temperature is: ' + str(cpu.temperature) + 'C'
        message = temp_message
        requests.post(bot_chat+temp_message)
        writeLog()

    #Requesting all holdings
    if text == mycrypto and int((lastid)[0]) != message_id and userid in whitelist and chatid == botchat:
        holdings()
        send()
        writeLog()

    #Requesting bitcoin
    if text == mybtc and int((lastid)[0]) != message_id and userid in whitelist and chatid == botchat:
        crypto('btc')
        send()
        writeLog()
    
    #Error temperature
    if text == temp and host != 'raspberrypi' and int((lastid)[0]) != message_id and userid in whitelist and chatid == botchat:
        message = error_message4
        requests.post(bot_chat+error_message4)
        writeLog()

    #Help Command
    if text == help and int((lastid)[0]) != message_id and userid in whitelist and chatid == botchat:
        message = help_message
        requests.post(bot_chat+help_message)
        writeLog()

    #Easter Egg
    if (text == hitchhiker1 or text == hitchhiker2) and int((lastid)[0]) != message_id:
        message = hitchhiker_message
        requests.post(bot_chat+hitchhiker_message)
        writeLog()


    #Errors
    #Command Not Found
    if text not in tinydict and int((lastid)[0]) != message_id and userid in whitelist and chatid == botchat:
        message = error_message2
        requests.post(bot_chat+error_message2)
        writeLog()

    #User not allowed
    if int((lastid)[0]) != message_id and userid != myid:
        message = error_message3
        requests.post(bot_error+error_message3)
        writeLog()

    #Write DB File
    #writeDbFile()

    # Write to SQlite DB and close connection
    if message_id != int((lastid)[0]):
        writeId()
        print('Adding record to DB')
    else:
        print('Record already exists')

    #db.close()

    if verbose == "true":
        #print(json_data)
        #print(time)
        print(text)
        print(log_time)
        print("This is the message that we are getting from the JSON DATA: "+str(message_id))
        print("This is the last line that was written to the DB: "+str(lastid[0]))
        #print(userid)
        #print(new_id)
        #print (json.dumps(json_data,ensure_ascii=False,indent=2))

    time.sleep(2)
    #break
