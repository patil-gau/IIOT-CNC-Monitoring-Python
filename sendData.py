#*********This script is used to send all the IIOT data from device to server**************************
#importing of required libraries
from time import sleep 
import sqlite3 
import requests as req
from datetime import datetime
import configuration as config

#making a connection with the database
conn2=sqlite3.connect(config.DATABASENAME)
#create a cursor object to execute all sql queries
curs2=conn2.cursor()
curs2=conn2.execute('PRAGMA journal_mode=wal')
#temperory logging file
filename = "observationsData.txt"


#Function which sends AlarmInfo  data
#parameters :  endpoint - at which endpoint to send the data
#no return type for the fucntion
def SendAlarmData(endpoint):
   print("****************SENDING ALARM DATA********************")
   try:
      curs2.execute("select * from alarm ")
      result=curs2.fetchall()
      if result is not None: 
         data={}                   
         for colm in result:
            Id=colm[0]
            data["ID"]=colm[0]
            data["MachineID"]=colm[1]
            data["OperatorName"]=colm[2]
            data["JobID"]=colm[3]
            data["Shift"]=colm[4]
            data["Component"]=colm[5]
            data["ModelName"]=colm[6]
            data["Operation"]=colm[7]
            data["TimeStamp"]=colm[8]
            data["Reason"]=colm[9]
            data['ErrorCode']=colm[10]
            response=req.post(endpoint,data=data,timeout=2)
            if(response.status_code>=200 and response.status_code<=206):
               curs2.execute("delete from alarm where id=(?)",(Id,))
               conn2.commit()
               print("{} entry send to server and deleted from local database ").format(Id)
            else:
               print(response.status_code) 
               print("didnot get good response from server") 
               return                                    
      else:
         print("no data to send ...")
   except Exception as e:
      print("Exception occured SendAlarm : ",e)
      return


#Function which sends IdleTimeStamp and IdleTimeout data
#parameters :  IdleTimeStamp endpoint and IdleTimeout endpoint - at which endpoint to send the data
#no return type for the fucntion
def SendIdleTimeData(idleTimeStampDataEndpoint,idleTimeOutDataEndpoint):
   print("****************SENDING IDLE MINUTES DATA********************")
   try:
      #send the IdleTimeStamp data
      result = curs2.execute("select * from idle_timestamp ").fetchall()
      if result is not None:
         data={}                   
         for colm in result:
            Id=colm[1]
            data['machineId']=colm[4]
            data['timeStamp']=colm[2]
            data['idleMin'] = int(colm[3])
            data['empID'] = colm[0]
            data['reason']=colm[5]
            data['operatorName']=colm[6]
            data['modelName'] = colm[7]
            data['component'] = colm[8]
            data['operation']=colm[9]
            data['shift'] = colm[10]
            data['jobId'] = colm[11]
            data['startTime'] = str(colm[12])
            data['endTime'] = str(colm[13])
            response=req.post(idleTimeStampDataEndpoint,data=data,timeout=2)
            if(response.status_code>=200 and response.status_code<=206):
               curs2.execute("delete from idle_timestamp where id=(?)",(Id,))
               conn2.commit()
               print("{} entry send to server and deleted from local database ".format(Id))
            else:
               print(response.status_code) 
               print("didnot get good response from server") 
               return                              
      else:
         print("no data to send ...")

      # data from idleTimeout table
      curs2.execute("select * from idle_timeout")
      result=curs2.fetchall()
      if result is not None:
         data={}                   
         for colm in result:
            Id=colm[1]
            data['machineId']=colm[2]
            data['timeStamp']=colm[8]
            data['idleMin'] = int(colm[10])
            data['empID'] = colm[0]
            data['reason']=colm[9]
            data['operatorName']=colm[3]
            data['modelName'] = colm[6]
            data['component'] = colm[5]
            data['operation']=colm[7]
            data['shift'] = colm[4]
            data['jobID'] = colm[11]
            response=req.post(idleTimeOutDataEndpoint,data=data,timeout=2)
            if(response.status_code>=200 and response.status_code<=206):
               curs2.execute("delete from idle_timestamp where id=(?)",(Id,))
               conn2.commit()
               print("{} entry send to server and deleted from local database ".format(Id))
            else:
               print(response.status_code) 
               print("didnot get good response from server") 
               return        
                            
      else:
         print("no data to send ...")    
   except Exception as e:
      print("Exception occured SendIdleTime : ",e)
      return


#Function which sends production data
#parameters :  endpoint - at which endpoint to send the data
#no return type for the fucntion
def SendProductionData(endpoint):
   print("********************SENDING PRODUCTION DATA****************************")
   try:
      with open(filename,'a+') as f:
         curr_time = datetime.now()
         formatted_time = curr_time.strftime('%H:%M')
         print("$$$$$$$$$$$$$$$$$",formatted_time)
         if(str(formatted_time) == "6:00" or str(formatted_time) == "6:01" or str(formatted_time) == "6:02"):
            curs2.execute("delete from production")
            conn2.commit()
         curs2.execute("select * from production_status")
         idNo=curs2.fetchone()[1]
         print("Production Last value : " + str(idNo))
         curs2.execute("select * from production where id>(?) ",(idNo,))
         result=curs2.fetchall()           
         if result is not None:
            data={}                     
            for colm in result:
               Id=colm[0]
               data['empID'] = colm[14]
               data["ID"]=colm[0]
               data["OperatorName"]=colm[1]
               data["JobID"]=colm[2]
               data["Shift"]=colm[3]
               data["Component"]=colm[6]
               data["ModelName"]=colm[4]
               data["Operation"]=colm[5]
               data["CycleTime"]=float(colm[7])
               data["InspectionStatus"]=colm[8]
               data["Status"]=colm[9]
               data["TimeStamp"]=datetime.strptime(colm[10], '%Y/%m/%d %H:%M:%S') 
               data["MachineID"]=colm[11]
               response=req.post(endpoint,timeout=2,data=data)
               f.writelines([data['JobID'],'\t',data['Status'],'\t',str(data['TimeStamp']),str(result),'\n'])         
               if(response.status_code>=200 and response.status_code<=206):
                  curs2.execute("update production_status set value=(?) where id=(?)",(Id,1))
                  print("{} entry updated..".format(Id))
                  conn2.commit()                  
                  #request the PostOperatorLoginDetails to update
                  res=req.get("http://"+config.LOCALSERVER_IPADDRESS+":"+config.PORT+"/PostOperatorLoginDetails")
                  if(res.status_code>=200 and res.status_code<=206):
                     print("successfully sent PostOperatorLoginDetails")
                  else:
                     print("failure sent PostOperatorLoginDetails")   
               else:
                  print("didnot get good response from server")
                  return        
         else:
            print("no data to send ...")
      f.close()            
   except Exception as e:
            print("Exception occured Production : ",e)
            return
 
#Function Responsible for Sending Energy Meter Data
#parameters :  endpoint - at which endpoint to send the data
#no return type for the fucntion
def SendEnergyMeterData(endpoint):
   print("****************SENDING ENERGY METER DATA********************")
   try:
      curs2.execute("select * from energy_meter ")
      result=curs2.fetchall()
      if result is not None:
         with open('emlog.txt','a+') as em:
            for x in result: 
               #if end_energy value is 0.0 then dont send as end energy value is still not calculated
               if int(x[2]) == 0:
                  return
               data={}                   
               Id=x[0]
               data["startEnergyValue"]=x[1]
               data["endEnergyValue"]=x[2]
               data["totalEnergy"]=x[3]
               data["startTimeStamp"]=x[4]
               data['machineId'] = x[5]     
               response=req.post(endpoint,data=data,timeout=2)
               #temporary log for debugging energy meter issues
               em.writelines([str(data['startTimeStamp']),'\t',str(data['startEnergyValue']),'\t',str(data['endEnergyValue']),'\t',str(data['totalEnergy']),'\n'])
               em.close()
               if(response.status_code>=200 and response.status_code<=206):
                  curs2.execute("delete from energy_meter where id=(?)",(Id,))
                  conn2.commit()            
                  print("{} entry send to server and deleted from local database --> EnergyMeter".format(Id))
               else:
                  print(response.status_code) 
                  print("didnot get good response from server -->EnergyMeter") 
                  return                 
      else:
         #temporary log for debugging energy meter issues
         with open('emlog.txt','a+') as em:
            em.writelines(['No Data to send','\n'])
            em.close()        
         print("no data to send ...")
   except Exception as e:
      print("Exception occured EnergyMeter : ",e)
      return
   
   
#continously run the loop to send data to server every 5 seconds 
'''while(1):
    #Function call of 'SendProductionData' Function
    SendProductionData("http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/Production")

    #Function call of 'SendAlarmData' Function
    SendAlarmData("http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/AlarmInfo")

    #Function call of 'SendAlarmData' Function
    SendIdleTimeData("http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/PostIdleTime")
    
    #wait for 5 seconds 
    sleep(5)'''





