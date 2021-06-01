#!/usr/bin/python
# -*- coding: utf-8 -*-

# Any new command needs to be declared in the command list and added to the tinydic array

import os
import subprocess
import time
import datetime
import sys
import requests
import json
import configparser
import getpass
if os.system("uname -a | grep raspberry") == True:
    from gpiozero import CPUTemperature
else:
    pass

#Getting hostname
host = os.uname()[1]

#Getting username
user = getpass.getuser()

#Reading from the current path
path = __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

#Define your config, db and log file here
config_file = path+'/arousabot.conf'
pathTodb = path+'/dbId.db'
pathTolog = path+'/arousabot.log'

#Parsing config file
config = configparser.ConfigParser()
config.read(config_file)
apiKey = config['DEFAULT']['ApiKey']
botchat = int(config['CHATS']['botchat'])
myid = int(config['USERS']['myid'])
alexid = int(config['USERS']['alexid'])
faid = int(config['USERS']['faid'])
btcholdings = float(config['CRYPTO']['btcholdings'])
ethholdings = float(config['CRYPTO']['ethholdings'])
ltcholdings = float(config['CRYPTO']['ltcholdings'])
xrpholdings = int(config['CRYPTO']['xrpholdings'])


#Whitelist
whitelist=[myid,faid,alexid]

#Random Variables
log_time = datetime.datetime.now()

#Command List
ip = "/ip"
temp = "/temp"
all = "/all"
mycrypto = "/crypto"
mybtc = "/btc"
myeth = "/eth"
myltc = "/ltc"
myxrp = "/xrp"
help = "/help"
hitchhiker1 = "What's the meaning of life?"
hitchhiker2 = "What is the meaning of life?"

# If a command is not added here it will show as an error
tinydict = {ip,mycrypto,mybtc,myeth,myltc,myxrp,temp,help,hitchhiker1,hitchhiker2}

#Getting IP
#get_ip = requests.get('https://ipinfo.io/ip')

#GET JSON DATA from Telegram API

receive_data="https://api.telegram.org/bot"+str(apiKey)+"/GetUpdates?offset=-1&limit=1"


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
    elif coin == 'ltc':
        #print('LTC')
        operation = ltcholdings * price
        operation = int(operation)
        message = 'This is the value of your '+coin+' holdings: \n'+str(operation)+' €'
        #requests.post(bot_chat+message)
    elif coin == 'xrp':
        #print('XRP')
        operation = xrpholdings * price
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
    crypto('ltc')
    myltc = operation
    crypto('xrp')
    myxrp = operation
    all = mybtc + myeth + myltc + myxrp
    #message = 'This is the value of all your holdings: '+str(all)+' €'
    message = 'This is the value of all your holdings:\n BTC: '+str(mybtc)+' € \n ETH: '+str(myeth)+' € \n LTC: '+str(myltc)+' € \n XRP: '+str(myxrp)+' € \n TOTAL: '+str(all)+' €'

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
def readDb():
    global dbFile
    dbFile = open(pathTodb,'r')
    global readlastline
    readlastline = dbFile.readline()
    dbFile.close()

#Write DB function
def writeDb():
    dbFile = open(pathTodb,'w')
    dbFile.write(str(message_id))
    dbFile.close()

#Enable Logging
logging = 'false'

#Enable verbose mode
verbose = 'true'


while True:
    

    new_request = requests.get(receive_data) 
    json_data = new_request.json()

    
#Reading JSON Data
    try:
        text = json_data['result'][0]['message']['text'] # This gets the message
        message_id = json_data['result'][0]['message']['message_id'] # This gets the message_id to avoid re-sending data
        userid = json_data['result'][0]['message']['from']['id'] # This gets the user_id
        chatid = json_data['result'][0]['message']['chat']['id'] # This gets the chat_id
    except KeyError: #This deals with the exceptions
        print(datetime.datetime.now())
        print("An Exception has ocurred, will keep going")
        pass


    #Read DB File
    readDb()

    #POST MESSAGES only to my user or users in the whitelist
    bot_chat="https://api.telegram.org/bot"+str(apiKey)+"/sendMessage?chat_id="+str(userid)+"&text="

    #POST Messages to everyone else
    bot_error="https://api.telegram.org/bot"+str(apiKey)+"/sendMessage?chat_id="+str(chatid)+"&text="


    #Checking if message has been sent
    if int(readlastline) == message_id:
        print("Message has already been sent")
        time.sleep(2)
    #Sending Messages 
        
    #Successful messages

    #Requesting a IP
    if text == ip and int(readlastline) != message_id and userid in whitelist and chatid == botchat:
        #requests.post(bot_chat+ip_message)
        get_ip = requests.get('https://ipinfo.io/ip')
        ip_message = 'This is your ip: '+get_ip.text.strip('\n')
        requests.post(bot_chat+ip_message)
        writeLog()

    print(host)

    #Requesting temperature
    if text == temp and host == 'raspberrypi' and int(readlastline) != message_id and userid in whitelist and chatid == botchat:
        cpu = CPUTemperature()
        temp_message = 'CPU Temperature is: ' + str(cpu.temperature) + 'C'
        requests.post(bot_chat+temp_message)
        writeLog()

    #Requesting all holdings
    if text == mycrypto and int(readlastline) != message_id and userid in whitelist and chatid == botchat:
        holdings()
        send()
        writeLog()

    #Requesting bitcoin
    if text == mybtc and int(readlastline) != message_id and userid in whitelist and chatid == botchat:
        crypto('btc')
        send()
        writeLog()

    #Requesting ethereum
    if text == myeth and int(readlastline) != message_id and userid in whitelist and chatid == botchat:
        crypto('eth')
        send()
        writeLog()

    #Requesting litecoin
    if text == myltc and int(readlastline) != message_id and userid in whitelist and chatid == botchat:
        crypto('ltc')
        send()
        writeLog()

    #Requesting ripple
    if text == myxrp and int(readlastline) != message_id and userid in whitelist and chatid == botchat:
        crypto('xrp')
        send()
        writeLog()
    
    #Error temperature
    if text == temp and host != 'raspberrypi' and int(readlastline) != message_id and userid in whitelist and chatid == botchat:
        requests.post(bot_chat+error_message4)
        writeLog()

    #Help Command
    if text == help and int(readlastline) != message_id and userid in whitelist and chatid == botchat:
        requests.post(bot_chat+help_message)
        writeLog()

    #Easter Egg
    if (text == hitchhiker1 or text == hitchhiker2) and int(readlastline) != message_id:
        requests.post(bot_chat+hitchhiker_message)
        writeLog()


    #Errors
    #Command Not Found
    if text not in tinydict and int(readlastline) != message_id and userid in whitelist and chatid == botchat:
        requests.post(bot_chat+error_message2)
        writeLog()

    #User not allowed
    if int(readlastline) != message_id and userid != myid:
        requests.post(bot_error+error_message3)
        writeLog()

    #Write DB File
    writeDb()

    if verbose == "true":
        #print(json_data)
        #print(time)
        print(text)
        print(log_time)
        print("This is the message that we are getting from the JSON DATA: "+str(message_id))
        print("This is the last line that was written to the file: "+readlastline)
        #print(userid)
        #print(new_id)
        #print (json.dumps(json_data,ensure_ascii=False,indent=2))

    #time.sleep(2)
    break