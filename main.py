#import the library which reads all the cnc machine signals and stores in local database.
from signal_package import cncSignalsTracker
import configuration as conf
#importing api.py and sendData.py to creat paralell process
import flask_api.api as api_run
import liveStatusSendData as live_status_senddata
from time import sleep
import networkCheck as network_check

#importing multiprocessing library
import multiprocessing as mp  

database = conf.DATABASENAME
holdMachineEndpoint = "http://" + conf.LOCALSERVER_IPADDRESS + ":" + conf.PORT + "/HoldMachine"
localHeaders = conf.HEADERS

#create a cncSignalsTracker object
cnc = cncSignalsTracker()


def process_of_api():
    #start the server at port 5002
    api_run.app.run(port=5002,threaded=True)


#pass the configuration paramters 
#get all pin numbers from local db and assign it to raspberry pi
#starts the process of collecting signals from cnc machine
def process_of_main():
    cnc.configure(
        databaseName = database,
        headers = localHeaders,
        holdMachineUrl = holdMachineEndpoint
    )
    cnc.getAndSetupPins()
    cnc.start()
 
 
def process_of_livestatus_sendData():
    #continously run the loop to send data to server every 2 seconds 
    while(1):
        #Function call of 'SendLiveStatus' Function
        live_status_senddata.SendLiveStatus("http://"+conf.SERVER_IP+conf.SERVER_ENDPOINT_START+"/PostMachineStatus")        
        sleep(4)


def process_of_network_check():
    #call the check network connection from networkCheck file
    network_check.checkNetworkConnection()
    

if __name__  == "__main__":
    #Creating a multiprocesses of function
    p1 = mp.Process(target = process_of_api)
    p2 = mp.Process(target = process_of_main)
    p3 = mp.Process(target = process_of_livestatus_sendData)
    p4 = mp.Process(target = process_of_network_check)
     
    #Start executing the code inside the target function parllelly
    p1.start()
    p2.start()
    p3.start()
    p4.start()

    #wait until the completion of processes
    p1.join()
    p2.join()
    p3.join()
    p4.join()



