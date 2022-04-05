from ._globalVariables import LIVE_STATUS_CODES
import sqlite3 as sqlite


def configure(self,databaseName,headers,holdMachineUrl):
    self.DATABASE_NAME = databaseName
    self.HEADERS =  headers
    self.HOLD_MACHINE_URL = holdMachineUrl
    #make the database connection 
    databaseConnection(self,databaseName) 
    print("Configuration done.....")
    return  

def databaseConnection(self,database):
    CONNECTION = sqlite.connect(database)
    if CONNECTION:
        CURSOR = CONNECTION.cursor()
        CURSOR.execute('PRAGMA journal_mode=wal')
        print("ESTABLISHED CONNECTION SUCESSFULLY WITH DATABASE")
        self.connection = CONNECTION
        self.cursor = CURSOR
        #call getMachineIdFunction 
        loadMachineNameFromDB(self,)
        #call the initialSetupFunction
        initialSetup(self,)
        return
    else:
        print("FAILED TO ESTABLISH CONNECTION WITH DATABASE") 
        return None    


def initialSetup(self,):
   conn=self.connection
   curs=self.cursor
   machineId=self.machineId
   try:
      curs.execute("select * from live_status")
      result=curs.fetchone()[0]
      if result!=1:
         query="insert into live_status(machineId,machineType,status,color,signalName)values(?,?,?,?,?)"
         values=(machineId,"Automatic",LIVE_STATUS_CODES['machineIdle'],"orange","alarmON")
         curs.execute(query,values)
         conn.commit()
         print("live Status is set for the initial time")
      else:
         print("already the row exists")
   except Exception as e:
      print(e,"failed to insert to liveStatus for the initial time")


#GET THE MACHINE NAME FROM THE LOCAL DATABASE
def loadMachineNameFromDB(self,):
   conn=self.connection
   curs=self.cursor
   curs.execute("select * from other_settings")
   self.machineId=curs.fetchone()[1]
   print("machine Id set as = {}".format(self.machineId))
   return
   
