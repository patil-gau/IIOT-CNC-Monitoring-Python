#adminEndpoints.py
#This file is responsible for configuring the informations like machineID, serverIP and holding relay from the admin user.

#Functions and their descriptions
getServerIP():
	#This function is responsible for fetching the server ip from the local database.

serverConfiguration():
	#This function is responsible for updating the serverIP to the local database which is configured by the admin user on the admin dashboard.

UpdateNetworkDetails():
	#This function is responsible for network configuration
	#This updated the ip, dns and gateway to localdatabase

UpdateSignalsDetails():
	#This function is responsible for updating the signals details configured from the admin user on admin dashboard

getNetworkConf():
	#This function is responsible for fetching the network configurations like ip, dns and gateway from the networkConf table of the "erp.db"

otherSettings():
	#This function is responsible for updating the informations machineId, batchsize, holdingRelay, machineBypass, idleTimeout, cleaningInteval and machineType.

getOtherSettings():
	#This function is responsible for fetching the information present in the otherSettings table of the "erp.db"

