#main.py
#This file is responsible for calling the functions of the api.py, networkCheck.py and sendData.py using parallel process method.

#Functions and their description
process_of_main():
	#This function is responsible for doing the initial setup of raspberry pi.
	#This calls the functions inside cncSignalsTracker.py and configuration.py
	#This functions calls the function inside networkCheck.py
	
process_of_api():
	#This function is responsible for running the flask app and api.py.

process_of_sendData():
	#This function is responsible for calling the functions inside of sendData.py.
	#It calls 3 functions for sending liveStatus data, alarm data and production data.
	#This will call the functions every 4 seconds.
process_of_network_check():
	#This function will check the internet connection between the local machine and the server.
	#It will call the function inside networkCheck.py.

#All the above functions will run parallelly using multiprocessing module.

