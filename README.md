# ArousaBot

## Changelog

### 04/06/2021

* The bot now writes/reads the messageid, user, command, message and date to a DB

### 03/06/2021

* Created a second module for Backup Monitoring

### 01/06/2021

* Added a way to deal with no internet exception

### 03/12/2020

* Added function for ETH, LTC, XRP and total crypto

### 02/12/2020

* Added function to check BTC holdings

### 18/10/2020

* Modified IP request in order to reduce the number of requests sent to the server

### 22/05/2020

* Added temperature command
* Reading config file in same directory

### Pending

* Add option to run the backup manually
* Add RemindMe function
* Use the logging python module instead of creating own logging function


## Bugs

If the dbId.db is empty the whole process fails - This is solved now as we are using a SQLITE db