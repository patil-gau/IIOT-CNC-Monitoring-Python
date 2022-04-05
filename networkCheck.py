#This file is responsible to check if we can connect to the server or not.
#It indicates network status on the device
import RPi.GPIO as GPIO
import subprocess
from time import sleep
GPIO.setmode(GPIO.BOARD)
GPIO.setup(36,GPIO.OUT)

#check function will check if we are connected to network
def checkNetworkConnection():
    flag = 1
    while(1):
        sleep(5)    
        result=subprocess.Popen("sudo mii-tool eth0 ",stdout=subprocess.PIPE,shell=True)
        finalResult=result.communicate()
        if (b'eth0: no link\n' in finalResult and flag == 0):
            #make the led off on the device
            GPIO.output(36,False)
            print("led off")
            flag = 1
        else:
            #on the led on the device
            GPIO.output(36,True)
            print("led on")
            flag = 0
