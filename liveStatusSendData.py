#importing of required libraries
from time import sleep 
import sqlite3 
import requests as req
import configuration as config

#making a connection with the database
conn2=sqlite3.connect(config.DATABASENAME)

#create a cursor object to execute all sql queries
curs2=conn2.cursor()
curs2=conn2.execute('PRAGMA journal_mode=wal')


#Function which sends liveStatus data
#parameters :  endpoint - at which endpoint to send the data
#no return type for the fucntion
def SendLiveStatus(endpoint):                    
    print("****************SENDING LIVE SIGNALS DATA********************")
    try:
        curs2.execute("select * from live_status")
        result=curs2.fetchone()
        if result is not None: 
            Id=str(result[0])
            machineId=result[1]
            machineType=result[2]
            status=str(result[3])
            signalColor=result[4]
            signalName=result[5]
            response=req.post(endpoint+"?ID="+Id+"&MachineID="+machineId+"&MachineType="+machineType+"&Status="+status+"&SignalName="+signalName+"&SignalColor="+signalColor,timeout=2)
            if(response.status_code>=200 and response.status_code<=206):
                print("Current Live Status : {}".format(signalName))
                print(" Live Status data successfully sent ")
            else:
                 print("didnot get good response from server")
                 return             
        else:
            print("no data to send....")
    except Exception as e:
        print("Exception occured : ",e)
        return