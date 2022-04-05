#api.py

#This file is responsible for creating interaction between main.py and react app

#This file configures the holding pin
holding pin = 5 #this pin is fetched from the local database (Table = OtherSettings
holding pin = 7 #if failed to fetch the holding pin from the local database set the holding pin number manually as pin number 7

#Functions and their description
->shutdown():	
	#This function is to shutdown the machine from the operator screen.
	#On clicking the shutdown button in react app machine will get turn off

->hold_machine():	
	#This function makes the machine hold or releases the machine from hold condition.
	#This function the makes the holding pin high and low.
			
->returnCurrentSignal():			
	#This function is responsible for getting the current signal from the local database("erp.db").
	#liveSignals are stored in the liveStatus table of the "erp.db" file.
	#And afte fetching the liveSignal, the same signal will be reflected in the operator screen.

