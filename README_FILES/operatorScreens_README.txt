#operatorScreens.py
#This file is responsible for loading the operator screen on the react app
#This file allows the user to login on the react app

#Fucntions and their description
login():
	#This function helps the user to login to the operator screen

loadScreen():
	#This function is responsible for storing the shift data to local database
	#And it is rsponsible for getting the server ip from the local database

operatorScreen():
	#This function is responsible for displaying all the informations like machineId, operatorName, component, model, operation.
	#Calculates the current shift
	#Releases the machine from the holding condition
	#Inserts production data to the local database when the operator enters the jobid and submits

alarmScreen():
	#This function is responsible for storing alarm data to the local database.

IdleTimeout():
	#This function is responsible for storing the machine idle timeout data to local database

