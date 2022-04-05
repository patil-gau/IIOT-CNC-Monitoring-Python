from datetime import datetime,date
import requests as req
from sqlalchemy.sql.functions import mode
from ._globalVariables import PRODUCTION_ARRAY
from ._holdMachine import holdMachine
import RPi.GPIO as GPIO
import time
import sendData as data_sending_function
import configuration as config
from pymodbus.client.sync import ModbusSerialClient
import numpy as np
from liveStatusSendData import SendLiveStatus

#SET BOARD MODE TO BCM
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11,GPIO.OUT)

#PRODUCTION MATCHING ARRAY
#PRODUCTION_ARRAY=["cycleON","cycleOFF"]

#START A MODBUS CLIENT
client= ModbusSerialClient(method = "rtu", port="/dev/ttyUSB0",stopbits = 1, bytesize = 8, parity = 'E', baudrate=19200)

#DICTONARY WHICH STORES THE DEFAULT STATUS VALUES FOR EVERY LIVE STATUS SIGNAL
LIVE_STATUS_CODES =  {
    "machineIdle" : 0,
    "cycle" : 2,
    "emergency" : 3,
    "alarm" : 4
       }

#global FLAG VARIABLES WHICH KEEPS A TRACK OF STATUS OF THE EVERY SIGNAL , WHETHER THE SIGNAL IS ON OR OFF
#FLAG = 0  SIGNAL IS OFF 
#FLAG = 1 SIGNAL IS ON
cycleflag=0
spindleflag=0
resetflag=0
emergencyflag=0
alarmflag=0
runoutnotokflag=0
machineflag=0
m30flag=0
idleStartTime = None
idleEndTime = None
cycleStartTime = None
cycleEndTime = None
idleStartTimeStamp = None
idleEndTimeStamp = None
start_active_power_total = 0.0
end_active_power_total = 0.0
total_energy = 0.0

TEMP_PRODUCTION_ARRAY =  []

#THIS FUNCTION WILL READ THE CURRRENT SIGNAL FROM THE CNC MACHINE
#PARARMS: INPUT PIN : PIN TO READ THE CURRRENT SIGNAL
#         PROCESS ON : CHECK IF SIGNAL IS ON 
#         PROCESS OFF : CHECK IF SIGNAL IS OFF
#RETURN TYPE : NONE
def getCurrentSignal(self,InputPin,processOn,processOff):
    global idleEndTime,idleStartTime,cycleStartTime,cycleEndTime,idleStartTimeStamp,idleEndTimeStamp,start_active_power_total,end_active_power_total,total_energy
    flag=getFlagStatus(processOn)
    
    #Read signal from the Raspberry pi 
    SignalStatus=GPIO.input(InputPin)
    
    #check the time at which this signal is raised
    timeObj = datetime.now()
    timeStamp=timeObj.strftime("%Y/%m/%d %H:%M:%S")
    
    #signal on conditions
    if(flag == 0 and SignalStatus==1):
        process=processOn
        print(process)
        print(timeStamp)
        setFlagStatus(process,1)
        insertSignalToLocalDb(self,self.machineId,process,timeStamp)
        if process=="alarmON":
            GPIO.output(11, True)
            updateLiveStatus(self,LIVE_STATUS_CODES['alarm'],"Alarm","red")
            holdMachine(self,)
            jobProgress(self,"finished")
            
            #send liveStatus data to server 
            SendLiveStatus("http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/MachineStatus")
        elif process=="machineON":
            idleStartTime = time.time()
            idleStartTimeStamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            updateLiveStatus(self,LIVE_STATUS_CODES['machineIdle'],"Machine Idle","orange")
            holdMachine(self,)
            
            #send liveStatus data to server 
            SendLiveStatus("http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/MachineStatus")
            
            #get the current power form energy meter
            register_values = readRegisterValues(self,start_address=2699,count_value=2)
 
            #only when energy meter is connected do following
            if(register_values!=-1):              
               #check if already start energy is stored -> returned 0.000 if no start_energy_value
               start_active_power_total=fetchStartEnergy(self,)
               end_active_power_total = register_values[0] 
               print("end_active_power_total",end_active_power_total)
               if(start_active_power_total!=0.000):
                  print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                  total_energy = end_active_power_total - start_active_power_total
                  #update the exiting row
                  updateEnergyMeterData(self,end_active_power_total,total_energy)
                  #send the updated energy meter data to server
                  data_sending_function.SendEnergyMeterData("http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/PostEnergyMachinewiseDetails")
                  #set start energy value and create new row 
                  start_active_power_total=end_active_power_total
                  insertEnergyMeterData(self,start_active_power_total,timeStamp,self.machineId)
               else:
                  #fetch statrt energy value and insert a new row
                  start_active_power_total=end_active_power_total
                  insertEnergyMeterData(self,start_active_power_total,timeStamp,self.machineId)
        elif process=="emergencyON":
            GPIO.output(11, True)
            updateLiveStatus(self,LIVE_STATUS_CODES['emergency'],"Emergency","red")
            jobProgress(self,"finished")
            #send liveStatus data to server 
            SendLiveStatus("http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/MachineStatus")
        elif process=="cycleON":
            GPIO.output(11,False)
            idleEndTime = time.time()
            idleEndTimeStamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            idleSeconds=idleEndTime-idleStartTime
            insertIdleTimeStampsToLocalDb(self,self.machineId,timeStamp,idleSeconds,idleStartTimeStamp,idleEndTimeStamp)
            cycleStartTime = time.time()
            TEMP_PRODUCTION_ARRAY.clear()
            TEMP_PRODUCTION_ARRAY.append(process)
            updateLiveStatus(self,LIVE_STATUS_CODES['cycle'],"Cycle","green")
            #update progress of job as job running
            jobProgress(self,"running")
            #send liveStatus data to server 
            SendLiveStatus("http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/MachineStatus")
            #send the updated energy meter data to server
            data_sending_function.SendEnergyMeterData("http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/PostEnergyMachinewiseDetails")                          
        else:
            pass

 
    #signal off  condition
    if(flag == 1 and SignalStatus == 0):
        process=processOff
        print(process)
        print(timeStamp)
        setFlagStatus(process,0)
        insertSignalToLocalDb(self,self.machineId,process,timeStamp)
        if (process=="emergencyOFF" or process=="cycleOFF" or process=="alarmOFF"):
            updateLiveStatus(self,LIVE_STATUS_CODES['machineIdle'],"Machine Idle","orange") 
            holdMachine(self,)
            #send liveStatus data to server 
            SendLiveStatus("http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/MachineStatus")
            #Function call of 'SendAlarmData' Function
            data_sending_function.SendAlarmData("http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/AlarmInfo")

        if (process=="cycleOFF"):
            #update progress of job has finished
            GPIO.output(11, True)
            idleStartTime = time.time()
            idleStartTimeStamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cycleEndTime = time.time() 
            cycleTime=cycleEndTime-cycleStartTime
            updateCycleTime(self,cycleTime)
            productionOk(self,"finished")
            # falling functions which send data after cycle off signal
            #Function call of 'SendProductionData' Function
            data_sending_function.SendProductionData("http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/Production")
            #Function call of 'SendAlarmData' Function
            #Parameter 1 is for idleTimeStamp 
            #Paramter 2 is endpoint for sending idleTimeOut Data
            data_sending_function.SendIdleTimeData("http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/PostIdleTime","http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/PostIdleTimeOut")
            
        #<-------- old logic to consider production only when m30 signal comes  --------->
        # 
        # elif process=="m30OFF":
        #     TEMP_PRODUCTION_ARRAY.append(process)
        #     if(PRODUCTION_ARRAY==TEMP_PRODUCTION_ARRAY[0:2]):
        #        print("Array matched")
        #        #make production status as 1 and progress as job finished
        #        productionOk(self,"finished")

        # else:
        #     pass

        #<-------------------------------------------------------------------------------->


#THIS FUNCTION SAVES SIGNAL DATA IN LOCAL DB
#PARAMS : MACHINE ID : ON WHICH MACHINE THIS SIGNAL WAS GENERATED
#         PROCESS : PROCESS OF SIGNAL
#         TIME : TIME OF SIGNAL
#RETURN TYPE : NONE
def insertSignalToLocalDb(self,machineId,process,timeStamp):       
      sql="INSERT INTO signals(machineId,process,timeStamp) VALUES(?,?,?)"               
      values=(machineId,process,timeStamp)
      try:
          if(self.cursor.execute(sql,values)):
              self.connection.commit()              
              print("successfully inserted into local database")
      except Exception as e:          
          print(e)
          print("unable to insert into local database")


#THIS FUNCTION SAVES PRODUCTION DATA IN LOCAL DB
#PARAMS : PROCESS : PROCESS OF SIGNAL
#RETURN TYPE : NONE
def productionOk(self,progress):
      data=self.cursor.execute("SELECT MAX(id) FROM production")
      lastId=self.cursor.fetchone()[0]
      sql="update production set status=?,progress=? where id=?"
      values=("1",progress,lastId)
      try:          
          result=self.cursor.execute(sql,values)
          self.connection.commit()
          print("updated status  1 to last production job ")         
      except Exception as e:       
          print(e)  
          print("failed to update status  1 to last production job")


#THIS FUNCTION SAVES STATUS OF JOB DATA IN LOCAL DB.
#JOB STATUS CAN BE STARTED|RUNNING|FINISHED
#PARAMS : PROCESS : STATUS OF JOB
#RETURN TYPE : NONE
def jobProgress(self,progress):
      data=self.cursor.execute("SELECT MAX(id) FROM production")
      lastId=self.cursor.fetchone()[0]
      sql="update production set progress=? where id=?"
      values=(progress,lastId)
      try:
          result=self.cursor.execute(sql,values)
          self.connection.commit()
          print("updated progress as {} to last production job ".format(progress))         
      except  Exception as e:         
          print(e)   
          print("failed to update progress of job to last production job")


#THIS FUNCTION UPDATES LIVE STATUS DATA IN LOCAL DB.
#PARAMS :  CODE : STATUS CODE ASSIGNED TO SIGNAL
#          SIGNAL:SIGNAL NAME
#          COLOR:COLOR FOR SIGNAL TO INDICATE
#RETURN TYPE : NONE
def updateLiveStatus(self,status,signal,color):
      try:
         query = "update live_status set status=?,signalName=?,color=? where id=?" 
         values = (status,signal,color,1) 
         self.cursor.execute(query,values) 
         self.connection.commit()
         print("live status machine idle updated")  
      except Exception as e:
         print(e)
         print("failed to update live status")          


#THIS FUNCTION UPDATES FLAG STATUS OF EVERY SIGNAL.
#PARAMS :  PROCESS : PROCESS OF SIGNAL
#RETURN TYPE : BOOLEAN VALUE OF FLAG STATUS OF THE PROCESS
def getFlagStatus(process):
          global cycleflag,spindleflag,machineflag,m30flag,resetflag,emergencyflag,alarmflag,runoutnotokflag
          if(process=="cycleON" or process=="cycleOFF"):
              return cycleflag
          elif(process=="spindleON" or process=="spindleOFF"):
              return spindleflag
          elif(process=="machineON" or process=="machineOFF"):
              return machineflag
          elif(process=="m30ON" or process=="m30OFF"):
              return m30flag
          elif(process=="resetON" or process=="resetOFF"):
              return resetflag
          elif(process=="emergencyON" or process=="emergencyOFF"):
              return emergencyflag
          elif(process=="alarmON" or process=="alarmOFF"):
              return alarmflag
          else:
              return  runoutnotokflag


#THIS FUNCTION SET'S FLAG STATUS OF EVERY SIGNAL.
#PARAMS :  PROCESS : PROCESS OF SIGNAL
#          FLAG: BOOLEAN VALUE OF  FLAG STATUS TO UPDATE
#RETURN TYPE : BOOLEAN VALUE OF FLAG STATUS OF THE PROCESS
def setFlagStatus(process,flag):
          global cycleflag,spindleflag,machineflag,m30flag,resetflag,emergencyflag,alarmflag,runoutnotokflag
          if(process=="cycleON" or process=="cycleOFF"):
              cycleflag=flag
              return cycleflag
          elif(process=="spindleON" or process=="spindleOFF"):
              spindleflag=flag
              return spindleflag
          elif(process=="machineON" or process=="machineOFF"):
              machineflag=flag
              return machineflag
          elif(process=="m30ON" or process=="m30OFF"):
              m30flag=flag     
              return m30flag
          elif(process=="resetON" or process=="resetOFF"):
              resetflag=flag     
              return resetflag
          elif(process=="emergencyON" or process=="emergencyOFF"):
              emergencyflag=flag     
              return emergencyflag
          elif(process=="alarmON" or process=="alarmOFF"):
              alarmflag=flag     
              return alarmflag
          else:
              runoutnotokflag=flag
              return  runoutnotokflag 


#THIS FUNCTION DAVES IDLETIMESTAMP DATA TO DB.
#PARAMS :  MACHINEID : MACHINE NAME 
#          TIMESTAMP: TIME OF SIGNAL
#          IDLEMINUTES: DURATION OF IDLE TIME OF MACHINE
#          IDLESTARTTIME: START TIME OF IDLE TIME OF MACHINE
#          IDLEENDTIME: END TIME OF IDLE TIME OF MACHINE
#RETURN TYPE : BOOLEAN VALUE OF FLAG STATUS OF THE PROCESS
def insertIdleTimeStampsToLocalDb(self,machineId,timeStamp,idleMinute,idleStartTime,idleEndTime):       
      res = req.get("http://"+config.LOCALSERVER_IPADDRESS+":"+config.PORT+"/getsessiondata")
      result = res.json()['result']
      operatorName = result['OperatorName'] 
      empId = result['EmpId'] 
      jobId = result['JobId'] 
      shift = result['Shift']
      model = result['Model']
      component = result['Component']
      operation = result['Operation']
      sql="INSERT INTO idle_timestamp(emp_id,machine_id,timestamp,idle_min,reason,operatorName,modelName,component,operation,shift,jobId,start_time,end_time) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)"               
      values=(empId,machineId,timeStamp,str(round(idleMinute,2)),"Production Idle",operatorName,model,component,operation,shift,jobId,idleStartTime,idleEndTime)      
      try:
          if(self.cursor.execute(sql,values)):

              self.connection.commit()
              print("successfully inserted idletimeStamps into local database")
      except Exception as e:
        
          print(e)
          print("unable to insert idletimeStamps into local database")               


#THIS FUNCTION UPDATES CYCLE TIME OF A SIGNAL
#PARAMS :  CYCLETIME : TIME IN SECONDS
#RETURN TYPE : NONE
def updateCycleTime(self,cycleTime):
      try:
          data=self.cursor.execute("SELECT MAX(id) FROM production")
          lastId=self.cursor.fetchone()[0]
          sql="update production set cycleTime=? where id=?"
          values=(str(round(cycleTime,2)),lastId)
          result=self.cursor.execute(sql,values)
          self.connection.commit()
          print("updated cycle time  ")
      except  Exception as e:
        
          print(e)   
          print("failed to update cycle time")


#THIS FUNCTION READS ENERGY VALUE FROM ENERGY METER
#PARAMS :  START_ADDRESS : START REGISTER ADDRESS
#          COUNT_VALUE : INT : NUMBER OF REGISTERS TO READ
#RETURN TYPE : FLOAT ARRAY ELSE -1 IF ENERGY METER NOT CONNECTED
def readRegisterValues(self,start_address,count_value):
    try:
        res = client.read_holding_registers(address=start_address,count=count_value, unit=1)
        val=res.registers
        d16 = np.array(val, dtype=np.int16)
        tmp = np.array([d16[1], d16[0]], dtype=np.int16)
        tmp.dtype = np.float32
        client.close()
        print(f"Value read from register is {val}")
        return tmp,1  # return 1 to indicate energy meter status
    except Exception as e:
        print("Exception in reading ",e)       # return 0 to indicate energy meter is not connected
        client.close()
        return -1
            

#THIS FUNCTION INSERTS ENERGY DATA OF MACHINE TO DB.
#PARAMS :  START_ENERGY : ENERGY DURING MACHINE START
#          START_TIME : START TIME OF MACHINE
#          MACHINEID : MACHINE NAME 
#RETURN TYPE : NONE
def insertEnergyMeterData(self,start_energy_value,start_timestamp,machineId):
      sql="INSERT INTO energy_meter(start_energy_value,end_energy_value,total_energy,start_timestamp,machine_id) VALUES(?,?,?,?,?)"               
      values=(float(start_energy_value),0.0,0.0,start_timestamp,machineId)
      try:
          if(self.cursor.execute(sql,values)):
              self.connection.commit()
              print("energy start values saved in local database")
      except Exception as e:
          print(e)
          print("failed to record start values of energy meter")

#THIS FUNCTION UPDATES ENERGY OF MACHINE IN DB WHEN IT WAS SHUTDOWN.
#PARAMS :  END_ENERGY : ENERGY DURING SHUTDOWN
#          TOTAL_ENERGY: START ENERGY OF MACHINE - END ENERGY OF MACHINE
#RETURN TYPE : NONE
def updateEnergyMeterData(self,end_energy_value,total_energy):
    try:
          data=self.cursor.execute("SELECT MAX(id) FROM energy_meter")
          if(data!= None):
            lastId=self.cursor.fetchone()[0]
            sql="update energy_meter set end_energy_value=?,total_energy=? where id=?"
            values=(float(end_energy_value),total_energy,lastId)
            self.cursor.execute(sql,values)
            self.connection.commit()
            print("updated energy_meter end values  ")
    except  Exception as e:
          print(e)   
          print("failed to updated energy_meter end values")

#THIS FUNCTION FETCHES THE ENERGY WHEN MACHINE WAS STARTED FOR A DAY FROM DB.
#RETURN TYPE:FLOAT VALUE OF START ENERGY
def fetchStartEnergy(self,):
    try:
        result=self.cursor.execute("SELECT MAX(id) FROM energy_meter")
        if(result!=None):
            lastId=result.fetchone()[0]
            sql="select * from energy_meter where id=?"
            values=(lastId,)
            self.cursor.execute(sql,values)
            return self.cursor.fetchone()[1]
        else:
            return 0.000
    except Exception as e:
        print(e)
        #returning None for no data to fetch
        return 0.000

    


