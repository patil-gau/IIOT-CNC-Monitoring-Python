import requests as req
import json

#THIS FUNCTION IS RESPONSIBLE FOR HOLDING THE CNC MACHINE
def holdMachine(self,):
      HOLD_MACHINE_URL = self.HOLD_MACHINE_URL
      LOCAL_HEADER = self.HEADERS
      try:
         result=req.post(HOLD_MACHINE_URL,json.dumps({"State":"Hold"}),headers=LOCAL_HEADER,timeout=2)
         print("holding machine")                
      except Exception as e:
         print(e)