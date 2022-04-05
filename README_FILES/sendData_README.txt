#sendData.py
#This file is responsible for sending the liveSignals data, alarm data and production data from local database to server.

#Functions and their descriptions
SendAlarmData():
	#This function is responsible for sending the alarm data store in the alarm table of the local database "erp.db"
	#Once the data has been sent to the server, the sent data will be deleted immediately from the local database.

SendLiveStatus():
	#This function is responsible for sending the live status data like machine idle, cycle, alarm and emergency.
	#The data will be fetched from the liveStatus table of the localdatabase "erp.db" and sent to the server.

SendProductionData():
	#This function is responsible for sending the production data from the local database to the server.
	#Once the production data has been sent to the server, the sent data will be deleted after 24 hours from the local database.

