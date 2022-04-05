#GETTTING ALL THE ACTUAL PIN NUMBERS FROM DATABASE
import RPi.GPIO as GPIO

#THIS FUNCTIONS ASSIGNS INPUT PINS TO EVERY SIGNAL 
def getAndSetupPins(self):
   conn = self.connection
   curs = self.cursor
   print("FETCHING THE PINS AND SIGNAL NAMES FROM THE DATABASE.....")  
   curs.execute("SELECT * FROM pinout")
   for row in curs.fetchall():
      if(row[2] == "machine"):
          self.machineSignalInputPin = int(row[3]) 
      elif(row[2] == "cycle"):
          self.cycleSignalInputPin = int(row[3])
      elif(row[2] == "alarm"):
          self.alarmSignalInputPin = int(row[3])
      elif(row[2] == "emergency"):
          self.emergencySignalInputPin = int(row[3])
      elif(row[2] == "reset"):
          self.resetSignalInputPin = int(row[3])
      elif(row[2] == "m30"):
          self.m30SignalInputPin = int(row[3])
      elif(row[2] == "runoutnotok"):
          self.runOutNotOkSignalInputPin = int(row[3])
      elif(row[2] == "spindle"):
          self.spindleSignalInputPin = int(row[3])   

   print("Initilizing the gpio pins of raspberry pi .....")
   GPIO.setmode(GPIO.BOARD)
   GPIO.setup(self.machineSignalInputPin,GPIO.IN,pull_up_down = GPIO.PUD_UP)
   GPIO.setup(self.cycleSignalInputPin,GPIO.IN,pull_up_down = GPIO.PUD_UP)
   GPIO.setup(self.m30SignalInputPin,GPIO.IN,pull_up_down = GPIO.PUD_UP)
   GPIO.setup(self.emergencySignalInputPin,GPIO.IN,pull_up_down = GPIO.PUD_UP)
   GPIO.setup(self.resetSignalInputPin,GPIO.IN,pull_up_down = GPIO.PUD_UP)
   GPIO.setup(self.alarmSignalInputPin,GPIO.IN,pull_up_down = GPIO.PUD_UP)
   GPIO.setup(self.runOutNotOkSignalInputPin,GPIO.IN,pull_up_down = GPIO.PUD_UP)
   GPIO.setup(self.spindleSignalInputPin,GPIO.IN,pull_up_down = GPIO.PUD_UP)
   #setting gpio set warnings false 
   GPIO.setwarnings(False)

