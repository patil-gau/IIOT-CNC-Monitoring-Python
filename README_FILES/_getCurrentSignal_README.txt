#_getCurrentSignal.py
#This file is responsible for checking for the live signal, checking for the production and inserting live signals to local db. 

#Functions and their descriptions
getCurrentSignal():
	#This function is concerned about getting current live signal from the machine and inserting to local db, and also it checks for the production data by comparing the PRODUCTION_ARRAY and TEMP_PRODUCTION_ARRAY.
	#If both array matches then the production status is 1. If they do not match then the production status is 0.

insertSignalToLocalDb():
	#This function is responsible for inserting the live signals of the machine to local db.
	#All live signals will be inserted to signals table of the local database of "erp.db"

productionOk():
	#This function is responsible for checking production ok and inserting the production status to the local db.

jobProgress():
	#This function is responsible for tracking the production process. 
	#When machine is idle and operator enters jobid this function will update the progress column of the production table of the erp.db as "not yet started"
	#When the cycle is ON this updated the progress as "started"
	#When cycle or M30 becomes OFF this will insert the progress as "finished"

updateLiveStatus():
	#This function is to update the live status to the local db.
	#Live status -> machine Idle, cycle, alarm and emergency.

getFlagStatus():
	#This function is to check the which signal is ON or OFF and to maintain the flag for each signal.
	#If the flag is 0, then signal is OFF.
	#If the flag is 1, then signal is ON.

setFlagStatus():
	#This function is to set the signals flags after reading the current signal flag.
