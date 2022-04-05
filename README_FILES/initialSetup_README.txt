#initialSetup.py
#This file is concerned about configuring the database, creating connection to the database, loading machine name.

#Functions and their descriptions
configure():
	#This function is responsible for configuring the database name.

databaseConnection():
	#This function is responsible for creating connection to the local database ie, "erp.db"

initialSetup():
	#This function is responsible for inserting the live status data for the first time only if there is no data in the liveStatus table.

loadMachineNameFromDB():
	#This function is responsible for loading the machine name from otherSettings table of the local database "erp.db"
