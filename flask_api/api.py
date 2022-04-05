''' 
THIS FILE CONTAINS THE API ROUTES FOR REACT APPLICATION AND FOR THE  PYTHON FILES.
REFER THE MANUAL FOR THE DOCUMENTATION OF EVERY ENDPOINT
'''

#IMPORT ALL REQUIRED MODULES
from flask import Flask,request,jsonify,session
from sqlalchemy.sql.operators import Operators
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import exc,cast,Date,func,and_
import requests as req
import json
from datetime import datetime,timedelta,time
import RPi.GPIO as GPIO
from flask_cors import CORS, cross_origin
import configuration as config
from models import * 

#VARIABLE THAT HOLDS THE HOLDING RELAY PIN NUMBER
global holdingPin
EmpId=""
OperatorName=""
JobId=""
Shift=""
Model=""
Component=""
Operation=""
TimeStamp=""
MachineId=""
startTime = ""
endTime = ""
isActive = False
isAlarmDisabled = False

#VARIABLE THAT HOLDS THE HOLDING STATUS / BYPASS MACHINE OR HOLD MACHINE
holdingStatus = ""

#CREATE A APP OBJECT
app = Flask(__name__)

#CREATE A CORS OBJECT
cors = CORS(app)

#CONFIGURATION OF CORS AND AND SQLALCHEMY 
app.config['CORS_HEADERS'] = config.CORS_HEADERS
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.secret_key = config.SECRET_KEY

# #Things to add if get app not found error
# app.app_context().push()

#SQLALCHEMY DB OBJECT
db = SQLAlchemy(app)

#GET THE HOLDING PIN NUMBER AND HOLDING STATUS FROM LOCAL DATABASE
try : 
    result=otherSettings.query.get(1)
    holdingPin=int(result.holdingRelay)
    holdingStatus=result.machineBypass
    print(holdingPin)
    print(holdingStatus)
except Exception as e:
    print(e,"error getting status of holding Relay")
    #IF WE FAIL TO GET THE HOLDING CREDENTIAL THEN SET PIN 7 BY DEFAULT AS HOLDING PIN AND HOLDING STATUS AS BYPASS
    holdingPin=22
    holdingStatus="Hold Machine"

# GET UP GPIO PINS OF RASPBERRY PI
GPIO.setmode(GPIO.BOARD)
GPIO.setup(holdingPin,GPIO.OUT)


#SHUTDOWN FEATURE 
@app.route('/shutdown', methods=['GET'])
def shutdown():
   global startTime,isActive,EmpId,endTime
   isActive = False
   #send postOperationDetails 
   postOperatorLoginEndpoint = "http://" + config.SERVER_IP + config.SERVER_ENDPOINT_START + "/PostOperatorLoginDetails"
   headers = config.HEADERS 
   endTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   postOperatorLoginEndpointData = {
    "empID" : EmpId,
    "startTime" : startTime,
    "endTime" : endTime,
    "isActive" : isActive

    }          
   res=req.post(postOperatorLoginEndpoint,headers=headers,data=json.dumps(postOperatorLoginEndpointData),timeout=4)
   if res.status_code >=200 and res.status_code<=206:
        print("Operator Login Details posted successfully")
   else:
        print("Failed to post operator login details") 

   print("shutting down")   
   os.system("sudo shutdown -h now ") 
   return("",204)



#HOLDING MACHINE FEATURE
@app.route('/HoldMachine', methods=['POST'])
def hold_machine():
    data=request.get_json()
    state=data['State']
    if(holdingStatus=="Hold Machine"):
       if(state=='Hold'):
          print("holding machine....")
          GPIO.output(holdingPin,False)
       else:
          print("releasing machine....")
          GPIO.output(holdingPin,True) 
    else:
          #Bypass the machine
          GPIO.output(holdingPin,True)  
    return ("",204)


 
#RETURNS THE LIVE CURRENT SIGNAL ON MACHINE     
@app.route('/getCurrentSignal', methods=['GET', 'POST'])
def returnCurrentSignal():
  global isAlarmDisabled  
  username=request.get_json()['userName']
  #DEFAULT SIGNAL
  liveSignal = "Machine Idle"
  try:
      if isAlarmDisabled == False:
         result=liveStatus.query.get(1)
         if result is not None: 
            liveSignal=result.signalName
      else:
          liveSignal = "Maintenance Mode"     
  except Exception as e:
      print(e,"failed to get live Status code")        
  CurrentDate=datetime.now().date()
  CurrentTime=datetime.now().time()
  endTime=time(0, 00,00)
  sihTime=time(6, 59,00)
  if(CurrentTime>=endTime and CurrentTime<=sihTime):
      filterDate=CurrentDate-timedelta(1)
  else:
      filterDate=CurrentDate
  presentDate=filterDate.strftime("%Y-%m-%d")
  print(presentDate) 
  try:  
      productionCount=db.session.query(production).filter(and_(production.status.like("1"),production.operatorName.like(username),production.date.like(presentDate))).count()
      print(result) 
      return (jsonify({'result':{"status":1,"liveSignal":liveSignal,"production":productionCount}}))
  except:
      return (jsonify({'result':{"status":0,"liveSignal":liveSignal,"production":0}}))



###########OPERATOR SCREEN ENDPOINTS ###########
@app.route('/login', methods=['GET', 'POST'])
def login():
   global EmpId,OperatorName,startTime,isActive,endTime 
   machineId=request.get_json()['machineId']
   username=request.get_json()['username']
   password=request.get_json()['password']
   resultData={}
   #calculate the current shift
   TimeObj=datetime.now().time()
   print("Current Time :" + str(TimeObj))
   query=db.session.query(ShiftData).filter(and_(TimeObj>=func.time(ShiftData.fromTime),TimeObj<=func.time(ShiftData.toTime))) 
   for row in query.all():  
     if(row.id==1):
         print("Shift 1")
         resultData['Shift']=row.shift             
     elif(row.id==2):
         print("Shift 2")
         resultData['Shift']=row.shift 
     elif(row.id==3):
         print("Shift 3")
         resultData['Shift']=row.shift                         
     else:
         resultData['Shift'] = "not defined"

   #check for local admin user 
   if(username=="admin" and password=="IIotAdmin"):
         return jsonify({"result": {"status":1,"admin":True,"message":"success"}})   

   #check for a valid user or no       
   loginUrl="http://" + config.SERVER_IP + config.SERVER_ENDPOINT_START + "/Login"
   postOperatorLoginEndpoint = "http://" + config.SERVER_IP + config.SERVER_ENDPOINT_START + "/PostOperatorLoginDetails" 
   headers = config.HEADERS 
   try:
         res=req.post(loginUrl,headers=headers,data=json.dumps({"UserID":username,"Password":password,"MachineCode":machineId}),timeout=4)     
         componentList=[]
         modelList=[]
         data=res.json() 
         print(data)
         if(data['Error']!=None):
              print("error")    
              return jsonify({"result": {"status":0,"admin":False,"message":"invalid username or password"}}) 
         else:
              resultData['FullName']=data['FullName']
              data1=data['Components']
              data2=data['ProductModels']              
              EmpId = data['EmpCode']
              OperatorName = data['FullName']
              for datas in data1:
                 componentList.append(datas['Code'])
              for datas in data2:
                 modelObj={}
                 modelObj['code']=datas['Code']
                 modelObj['value']=datas['Value']   
                 modelList.append(modelObj)       
              resultData['Components']=componentList
              resultData['Models']=modelList
              resultData['EmpID'] = EmpId
              print(resultData)              
              #post OperatorLoginDetails
              isActive = True
              startTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
              endTime = startTime 
              postOperatorLoginEndpointData = {
                  "empID" : EmpId,
                  "startTime" : startTime,
                  "endTime" : endTime,
                  "isActive" : isActive

              }              
              res=req.post(postOperatorLoginEndpoint,headers=headers,data=json.dumps(postOperatorLoginEndpointData),timeout=4)
              if res.status_code >=200 and res.status_code<=206:
                 print("Operator Login Details posted successfully")
              else:
                  print("Failed to post operator login details")   
              
              
              return jsonify({"result": {"status":1,"admin":False,"message":"success","data":resultData}})      
         
   except Exception as e:         
         print("error while connecting to server for login details",e)
         return jsonify({"result": {"status":0,"admin":False,"message":"Something Went Wrong, Check Network Connection"}})

 
             
@app.route('/', methods=['GET', 'POST'])
def loadScreen():
   try:
       url="http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/ShiftList" 
       print(url)     
       res=req.get(url,timeout=4)
       datas=res.json()
       for data in datas: 
          idNew=data['ID']
          shiftNew=data['Name']
          fromTimeNew=data['FromTime']
          toTimeNew=data['ToTime']
          fromTimeNew=datetime.strptime(fromTimeNew,"%Y-%m-%dT%H:%M:%S")
          toTimeNew=datetime.strptime(toTimeNew,"%Y-%m-%dT%H:%M:%S")
          shiftObj=ShiftData(id=idNew,shift=shiftNew,fromTime=fromTimeNew,toTime=toTimeNew)
          try:
             result=ShiftData.query.filter_by(id=idNew).scalar() 
             if(result!=None):
                 pass
             else:    
                db.session.add(shiftObj)
                db.session.commit() 
                print("added shift data to datbase") 
          except Exception as e:
             print(e)
                     
   except:
       print("something went wrong while getting shift data...." )

    
   data={}
   try:
      result=otherSettings.query.get(1)
      if(result!=None):
          data['machineId']=result.machineId
          data['idleTimeout'] = result.idleTimeout
          data['batchSize']= result.batchSize
      else:
          print("no other settings data in database")

      #get the server ip from local database
      result=serverConf.query.get(1)
      if(result!=None):
          data['serverIp'] = result.ip
      else:
          print("no server ip data in database")

      return jsonify({"result": {"message":"success","status":1,"data":data}})      
   except Exception as e:
      print(e) 
      return jsonify({"result": {"messgae":"something went wrong","status":0,"data":{}}})



@app.route("/operator", methods=["GET", "POST"])
def operatorScreen():
    global EmpId,OperatorName,JobId,Shift,Model,Component,Operation,TimeStamp,MachineId
    result=request.get_json()
    shift=result['shift']
    username=result['fullName']
    component=result['componentName']
    model=result['modelName']
    operation=result['operationName']  
    machineId=result['machineId']
    jobId=result['jobId']
    #calculate the current shift
    TimeObj=datetime.now().time()
    query=db.session.query(ShiftData).filter(and_(TimeObj>=func.time(ShiftData.fromTime),TimeObj<=func.time(ShiftData.toTime))) 
    nowShift = ""
    for row in query.all():   
        if(row.id==1):
            print("Shift 1")
            nowShift=row.shift 
        elif(row.id==2):
            print("Shift 2")
            nowShift=row.shift  
        elif(row.id==3):
            print("Shidt 3")
            nowShift=row.shift
        else:
             pass                            

    timeObj = datetime.now()
    var_time=timeObj.strftime("%Y/%m/%d %H:%M:%S")
    CurrentDate=datetime.now().date()
    CurrentTime=datetime.now().time()
    sihTime=time(6, 59,59)
    if(CurrentTime<=sihTime):
         date=CurrentDate-timedelta(1)
    else:
         date=CurrentDate
    presentDate=date.strftime("%Y-%m-%d")
    OperatorName = username
    JobId = jobId
    Shift = shift
    Model = model
    Component= component
    Operation = operation
    TimeStamp = var_time
    MachineId = machineId    
    productionObj=production(operatorName=username,jobId=jobId,shift=shift,component=component,modelName=model,operation=operation,cycleTime="5.5",inspectionStatus="0",status="0",timeStamp=var_time,machineId=machineId,date=presentDate,progress="not started",emp_id=EmpId)
    with open('production.txt','a+') as f:
     try:
         db.session.add(productionObj)
         db.session.commit()
         f.writelines([jobId,"\t",str(var_time),"\n"])
         f.close()
         print("inserting into databse")
         print("releasing machine")
         releaseUrl="http://"+config.LOCALSERVER_IPADDRESS+":"+config.PORT+"/HoldMachine"
         headers = config.HEADERS
         res=req.post(releaseUrl,headers=headers,data=json.dumps({"State":"Release"}),timeout=2)         
         return jsonify({"result": {"status":1,"message":"job Status Ok , proceed to cycle ","data":{"shift":nowShift}}})
     except Exception as e:
         f.writelines([jobId,"\t",str(e),"\t",str(var_time),"\n"])
         f.close()
         print(e)
         return jsonify({"result": {"status":0,"message":"something went wrong please fill details once more","data":{}}})
         


@app.route('/alarmScreen', methods=['GET','POST'])
def alarmScreen():
    result=request.get_json()
    shift=result['shift']
    username=result['fullName']
    component=result['componentName']
    model=result['modelName']
    operation=result['operationName']  
    machineId=result['machineId']    
    reason=result['alarmReason']
    errorCode=result['errorCode']
    if result['jobId'] != "":
        jobId=result['jobId']
    else:
        jobId="No Job Placed"
    timeObj = datetime.now()
    time=timeObj.strftime("%Y/%m/%d %H:%M:%S")
    alarmObj=alarm(operatorName=username,jobId=jobId,shift=shift,component=component,modelName=model,operation=operation,timeStamp=time,machineId=machineId,reason=reason,errorCode=errorCode) 
    try:
         db.session.add(alarmObj)
         db.session.commit()
         print("inserting into database")
    except Exception as e:
         print(e)   
         db.session.rollback()
         return jsonify({"result": {"status":0,"message":"something went wrong"}})
    
    releaseUrl="http://"+config.LOCALSERVER_IPADDRESS+":"+config.PORT+"/HoldMachine"
    headers = config.HEADERS
    try:
          res=req.post(releaseUrl,headers=headers,data=json.dumps({"State":"Release"}),timeout=2)
          print(res.status_code)
    except:
          print("error..")  
          return jsonify({"result": {"status":0,"message":"something went wrong"}})   
    return jsonify({"result": {"status":1,"message":"successfully data saved"}})



@app.route('/idleTimeout', methods=['GET','POST'])
def IdleTimeout():
    global EmpId,JobId
    result=request.get_json()
    shift=result['shift']
    username=result['fullName']
    component=result['componentName']
    model=result['modelName']
    operation=result['operationName']  
    machineId=result['machineId']
    reason=result['idleReason']
    timeObj = datetime.now()
    time=timeObj.strftime("%Y/%m/%d %H:%M:%S")

    idleTimeoutObj=idleTimeout(emp_id=EmpId,operatorName=username,shift=shift,component=component,modelName=model,operation=operation,timeStamp=time,machineId=machineId,reason=reason,jobId=JobId) 
    try:
        db.session.add(idleTimeoutObj)
        db.session.commit()
        print("inserting into database")
    except Exception as e:
        print(e)   
        return jsonify({"result": {"status":0,"message":"something went wrong"}})

    releaseUrl="http://"+config.LOCALSERVER_IPADDRESS+":"+config.PORT+"/HoldMachine"
    headers = config.HEADERS
    try:
          res=req.post(releaseUrl,headers=headers,data=json.dumps({"State":"Release"}),timeout=2)
          print(res.status_code)
    except:
           print("error..")  
           return jsonify({"result": {"status":0,"message":"something went wrong"}})   
    return jsonify({"result": {"status":1,"message":"successfully data saved"}})



@app.route('/getsessiondata', methods=['GET'])
def getsessiondata():
    global EmpId,OperatorName,JobId,Shift,Model,Component,Operation,TimeStamp,MachineId
    dataToSend = {}
    dataToSend['OperatorName'] = OperatorName
    dataToSend['EmpId'] = EmpId
    dataToSend['JobId'] = JobId 
    dataToSend['Shift'] = Shift 
    dataToSend['Model'] = Model
    dataToSend['Component'] = Component
    dataToSend['Operation'] = Operation
    dataToSend['TimeStamp'] = TimeStamp
    dataToSend['MachineId'] = MachineId
    return jsonify({"result": dataToSend})



@app.route('/logout', methods=['GET'])
def Logout():
   global startTime,EmpId,OperatorName,JobId,Shift,Model,Component,Operation,isActive,endTime
   isActive = False
   #send postOperationDetails 
   postOperatorLoginEndpoint = "http://" + config.SERVER_IP + config.SERVER_ENDPOINT_START + "/PostOperatorLoginDetails"
   headers = config.HEADERS 
   endTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   postOperatorLoginEndpointData = {
    "empID" : EmpId,
    "startTime" : startTime,
    "endTime" : endTime,
    "isActive" : isActive
    }          
   res=req.post(postOperatorLoginEndpoint,headers=headers,data=json.dumps(postOperatorLoginEndpointData),timeout=4)
   if res.status_code >=200 and res.status_code<=206:
        print("Operator Login Details posted successfully")
   else:
        print("Failed to post operator login details")

   print("logging out...") 
   EmpId=""
   OperatorName=""
   JobId=""
   Shift=""
   Model=""
   Component=""
   Operation=""
   return jsonify({'result':'success'})     


@app.route('/PostOperatorLoginDetails', methods=['GET'])
def PostOperationLoginDetails():
    global startTime,EmpId,isActive,endTime
    postOperatorLoginEndpoint = "http://" + config.SERVER_IP + config.SERVER_ENDPOINT_START + "/PostOperatorLoginDetails"
    headers = config.HEADERS 
    endTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    postOperatorLoginEndpointData = {
    "empID" : EmpId,
    "startTime" : startTime,
    "endTime" : endTime,
    "isActive" : isActive
    }
    if(isActive):          
      res=req.post(postOperatorLoginEndpoint,headers=headers,data=json.dumps(postOperatorLoginEndpointData),timeout=4)
      if res.status_code >=200 and res.status_code<=206:
         print("Operator Login Details posted successfully")
      else:
         print("Failed to post operator login details")
    else:
        print("isActive False , user is logged out") 
    return("",200)        

#TOOL CHANGE FEATURE
@app.route('/ToolChange', methods=['GET'])
def ToolChange():
    global isAlarmDisabled
    print("Releasing Machine For Tool Change")
    GPIO.output(holdingPin,True) 
    isAlarmDisabled = True 
    return ("",204)

@app.route('/Maintenance', methods=['POST'])
def maintenance():
    global isAlarmDisabled
    result = request.get_json()
    response = {"status" : 0 , "message" :""}
    operator_id = result['operatorId']
    machine_id = result['machineId']
    operator_name = result['operatorName']
    time_stamp = result['timeStamp']
    reason = result['reason']
    try:
        MaintenanceObj = Maintenance(operator_id = operator_id, machine_id = machine_id, operator_name = operator_name, time_stamp = time_stamp, reason = reason)
        db.session.add(MaintenanceObj)
        db.session.commit()
        response["status"] = 1 
        response["message"] = "Data Saved Success"
    except Exception as e:
        response["status"] = 0
        response["message"] = str(e)

    isAlarmDisabled = False

    return jsonify(response)    


############### OPERATOR ENDPOINTS ENDS ###################





########## ADMIN ENDPOINTS ##############
@app.route('/getServerIP', methods = ['GET'])
def getServerIP():
    try:
        result = serverConf.query.get(1)
        if result != None:
            serverIp = result.ip
            print(serverIp)
            return jsonify({"result" : {"status" : 1, "data" : serverIp, "message" : "Success"}})
        else:
            return jsonify({"result" : {"status" : 1, "message" : "No previous data found", "data" : ""}})
    except Exception as e:
        print(e)
        return jsonify({"result" : {"status" : 0, "data" : "", "message" : "Failed"}})
 
 
       
@app.route('/updateServerIP', methods = ['POST'])
def serverConfiguration():
  endpoint = request.get_json()['endpoint'] 
  try:
      result=serverConf.query.filter_by(id = 1).scalar()
      if result != None:
          db.session.query(serverConf).filter(serverConf.id == 1).update({serverConf.ip:endpoint})
          db.session.commit()
          return jsonify({"result" : {"message" : "Server credentials updated successfully", "status" : 1}})
      else:
          serverConfObj = serverConf(id = 1,ip = endpoint)
          db.session.add(serverConfObj) 
          db.session.commit()
          return jsonify({"result" : {"message" : "Server credentials saved successfully", "status" : 1}})  
  except Exception as e:
      print(e)   
      return jsonify({"result" : {"message" : "something went wrong", "status" : 0}})
 
 
      
@app.route('/updateNetworkDetails', methods = ['POST'])
def UpdatenetworkDetails():
    ip = request.get_json()['ip']
    gateway = request.get_json()['gateway']
    dns = request.get_json()['dns']
    networkFileData = "interface eth0 \n static ip_address = {}\n static routers = {}\n static domain_name_servers = {}".format(ip, gateway, dns)
    print(networkFileData)
    try:
        result = networkConf.query.filter_by(id = 1).scalar()
        if result != None:
            db.session.query(networkConf).filter(networkConf.id == 1).update({"ip" : ip, "gateway" : gateway, "dns" : dns})
            db.session.commit()
            with open('/etc/dhcpcd.conf', 'w') as f:
                f.write(networkFileData)
                f.close()
            return jsonify({"result" : {"status" : 1, "message" : "Network details updated successfully"}})
        else:
            networkConfObject = networkConf(ip = ip, gateway = gateway, dns = dns)
            db.session.add(networkConfObject)
            db.session.commit()
            with open('/etc/dhcpcd.conf', 'w') as f:
                f.write(networkFileData)
                f.close()
            return jsonify({"result" : {"status" : 1, "message" : "Network details saved successfully"}})
    except Exception as e:
        return jsonify({"result" : {"status" : 0, "message" : "Something went wrong"}})


        
@app.route('/updateSignalsDetails', methods = ['POST'])
def UpdateSignalsDetails():
    resultList = []
    objinList = {}
    for i in range(1, 13):
        objinList["signal" + str(i)] = request.get_json()['signal' + str(i)]
        objinList["pin" + str(i)] = request.get_json()['pin' + str(i)]
        objinList["enable" + str(i)] = request.get_json()['enable' + str(i)]
        resultList.append(objinList)
        objinList = {}
    try:
        result = pinout.query.filter_by(signalName = 'cycle').scalar()
        if result != None:
            db.session.query(pinout).delete()
            db.session.commit()
        for i, data in enumerate(resultList):
            pinoutObject = pinout(machineId = "JG-20", signal = data['signal' + str(i + 1)], pin = data['pin' + str(i + 1)], status = data['enable' + str(i + 1)])
            db.session.add(pinoutObject)
            db.session.commit()
        return jsonify({"result" : {"status" : 1, "message" : "Network details saved successfully"}})
    except Exception as e:
        print(e)
        return jsonify({"result" : {"status" : 0, "message" : "Something went wrong"}})




@app.route('/getNetworkConf', methods = ['GET'])
def getNetworkConf():
    data = {}
    try:
        result = networkConf.query.get(1)
        if result != None:
            data['ip'] = result.ip
            data['dns'] = result.dns
            data['gateway'] = result.gateway
            return jsonify({"result" : {"status" : 1, "data" : data, "message" : "Successfully fetched and saved data"}})
        else:
            return jsonify({"result" : {"status" : 1, "message" : "No previous data found", "data" : {} }})
    except Exception as e:
        print(e)
        return jsonify({"result" : {"status" : 0, "data" : {}, "message" : "Failed"}})


        
@app.route('/updateOtherSettings', methods = ['POST'])
def otherSettingsFunction():
    data = request.get_json()
    machineId = data['machineId']
    batchSize = data['batchSize']
    holdingRelay = data['holdingRelay']
    machineBypass = data['machineBypass']
    idleTimeout = data['idleTimeout']
    cleaningInterval = data['cleaningInterval']
    machineType = data['machineType']
    try:
        result = otherSettings.query.filter_by(id = 1).scalar()
        if result != None:
            db.session.query(otherSettings).filter(otherSettings.id == 1).update({"machineId" : machineId, "batchSize" : batchSize, "holdingRelay" : holdingRelay, "machineBypass" : machineBypass, "idleTimeout" : idleTimeout, "cleaningInterval" : cleaningInterval, "machineType" : machineType})
            db.session.commit()
            return jsonify({"result" : {"status" : 1, "message" : "Other settings updated successfully"}})
        else:
         otherSettingsConfObject = otherSettings(machineId=machineId,batchSize=batchSize,holdingRelay=holdingRelay,machineBypass=machineBypass,idleTimeout=idleTimeout,cleaningInterval=cleaningInterval,machineType=machineType)
         db.session.add(otherSettingsConfObject)
         db.session.commit()
         return jsonify({"result": {"status" : 1,"message":"Other settings saved successfully"}})   
    except Exception as e:
        print(e)
        return jsonify({"result": {"status" : 0,"message":"Something went wrong"}})  



@app.route('/getOtherSettings', methods=['GET'])
def getOtherSettings():
   data={}
   try:
      result=otherSettings.query.get(1)
      if result!=None:
         data['machineId']=result.machineId
         data['batchSize']=result.batchSize
         data['holdingRelay']=result.holdingRelay
         data['machineBypass']=result.machineBypass
         data['idleTimeout']=result.idleTimeout
         data['cleaningInterval']=result.cleaningInterval
         data['machineType']=result.machineType         
         return jsonify({"result": {"status":1,"data":data,"message":"Successfully fetched saved data"}})
      else:
         return jsonify({"result":{"status":1,"message":"No previous data found","data":{}}})
   except Exception as e:
      print(e)
      return jsonify({"result":{"status":0,"data":{},"message":"Failed"}}) 

############### ADMIN ENDPOINTS ENDS ###################

#START THE SERVER AT PORT 5002 
'''if __name__ == "__main__":
    app.run(port=5002,threaded=True,debug=True)'''





