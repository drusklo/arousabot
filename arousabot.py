#!/usr/bin/python

import os
import subprocess
import time
import datetime
import sys
import requests
import json
import configparser
import getpass

#Getting username
user = getpass.getuser()

#Define your config file in here 
#config_file = '/home/'+str(user)+'/Playground/arousabot/arousabot.conf'
config_file = '/home/'+str(user)+'/python/arousabot/arousabot.conf'
config = configparser.ConfigParser()
config.read(config_file)
apiKey = config['DEFAULT']['ApiKey']
botchat = int(config['CHATS']['botchat'])
myid = int(config['USERS']['myid'])
alexid = int(config['USERS']['alexid'])
faid = int(config['USERS']['faid'])
pathTodb = config['PATHS']['pathTodb']
pathTolog = config['PATHS']['pathTolog']

#Whitelist
whitelist=[myid,faid,alexid]

#Random Variables
log_time = datetime.datetime.now()

#Command List
ip = "/ip"
help = "/help"
hitchhiker1 = "What's the meaning of life?"
hitchhiker2 = "What is the meaning of life?"

tinydict = {ip,help,hitchhiker1,hitchhiker2}

#Getting IP
get_ip = requests.get('https://ipinfo.io/ip')

#GET JSON DATA from Telegram API
receive_data="https://api.telegram.org/bot"+str(apiKey)+"/GetUpdates?offset=-1&limit=1"

#Messages
ip_message='This is your ip: '+get_ip.text.strip('\n')

help_message= "I need somebody"

hitchhiker_message = "42"

error_message="IP hasn't changed or the command is incorrect"

error_message2="Command not found"

error_message3="Trespassers will be shot, survivors will be shot again"

#Enable verbose mode
verbose = "true"

#Defining Logging function
def writeLog():
    logFile = open(pathTolog,'a')
    logFile.write(str(text))
    logFile.write(os.linesep)
    logFile.write(str(log_time))
    logFile.write(os.linesep)
    logFile.write(str(json_data))
    logFile.write(os.linesep)
    logFile.close()

#Defining Read DB function
def readDb():
    global dbFile
    dbFile = open(pathTodb,'r')
    global readlastline
    readlastline = dbFile.readline()
    dbFile.close()

#Defining Write DB function
def writeDb():
    dbFile = open(pathTodb,'w')
    dbFile.write(str(message_id))
    dbFile.close()


#Enable Logging
logging = "false"


while True:
    
    new_request = requests.get(receive_data)
    json_data = new_request.json()

    
#Reading JSON Data
    try:
        text = json_data['result'][0]['message']['text'] # This gets the message
        message_id = json_data['result'][0]['message']['message_id'] # This gets the message_id to avoid re-sending data
        userid = json_data["result"][0]["message"]["from"]["id"] # This gets the user_id
        chatid = json_data["result"][0]["message"]["chat"]["id"] # This gets the chat_id
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
        time.sleep(3)
    #Sending Messages 
        
    #Successful messages
    #Requesting a IP
    if text == ip and int(readlastline) != message_id and userid in whitelist and chatid == botchat:
        requests.post(bot_chat+ip_message)
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

    time.sleep(2)
    #break