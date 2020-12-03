#!/usr/bin/python

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
from gpiozero import CPUTemperature

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
mycrypto = "/crypto"
mybtc = "/btc"
myeth = "/eth"
myltc = "/ltc"
myxrp = "/xrp"
help = "/help"
hitchhiker1 = "What's the meaning of life?"
hitchhiker2 = "What is the meaning of life?"

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
btcprice = 'https://www.bitstamp.net/api/v2/ticker/btceur'

ethprice = 'https://www.bitstamp.net/api/v2/ticker/etheur'

ltcprice = 'https://www.bitstamp.net/api/v2/ticker/ltceur'

xrpprice = 'https://www.bitstamp.net/api/v2/ticker/xrpeur'

# Crypto function
def crypto():
    btc()
    eth()
    ltc()
    xrp()
    global totaloperation
    totaloperation = btcoperation + ethoperation + ltcoperation + xrpoperation

# BTC function
def btc():
    new_request = requests.get(btcprice)
    json_data = new_request.json()
    price = float(json_data['last'])
    global btcoperation
    btcoperation = btcholdings * price
    btcoperation = int(btcoperation)

# ETH function
def eth():
    new_request = requests.get(ethprice)
    json_data = new_request.json()
    price = float(json_data['last'])
    global ethoperation
    ethoperation = ethholdings * price
    ethoperation = int(ethoperation)
    
# ETH function
def ltc():
    new_request = requests.get(ltcprice)
    json_data = new_request.json()
    price = float(json_data['last'])
    global ltcoperation
    ltcoperation = ltcholdings * price
    ltcoperation = int(ltcoperation)

# ETH function
def xrp():
    new_request = requests.get(xrpprice)
    json_data = new_request.json()
    price = float(json_data['last'])
    global xrpoperation
    xrpoperation = xrpholdings * price
    xrpoperation = int(xrpoperation)


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
'''
#Reading Temperature Function (Only works in Raspberry Pi)
def readTemp():
    cpu = CPUTemperature()
    temp_message = 'CPU Temperature is: ' + str(cpu.temperature) + 'C'
'''

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

    #Requesting crypto
    if text == mycrypto and int(readlastline) != message_id and userid in whitelist and chatid == botchat:
        crypto()
        crypto_message = 'This is the total value of your holdings: '+str(totaloperation)+' €'
        requests.post(bot_chat+crypto_message)
        writeLog()

    #Requesting bitcoin
    if text == mybtc and int(readlastline) != message_id and userid in whitelist and chatid == botchat:
        btc()
        btc_message = 'This is the value of your BTC holdings: '+str(btcoperation)+' €'
        requests.post(bot_chat+btc_message)
        writeLog()

    #Requesting ethereum
    if text == myeth and int(readlastline) != message_id and userid in whitelist and chatid == botchat:
        eth()
        eth_message = 'This is the value of your ETH holdings: '+str(ethoperation)+' €'
        requests.post(bot_chat+eth_message)
        writeLog()

    #Requesting litecoin
    if text == myltc and int(readlastline) != message_id and userid in whitelist and chatid == botchat:
        ltc()
        ltc_message = 'This is the value of your LTC holdings: '+str(ltcoperation)+' €'
        requests.post(bot_chat+ltc_message)
        writeLog()

    #Requesting ripple
    if text == myxrp and int(readlastline) != message_id and userid in whitelist and chatid == botchat:
        xrp()
        xrp_message = 'This is the value of your XRP holdings: '+str(xrpoperation)+' €'
        requests.post(bot_chat+xrp_message)
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