from ._getCurrentSignal import getCurrentSignal

#FUNCTION CREATES A OBJECT OF EVERY SIGNAL AND CHECKS IF THAT SIGNALS STATUS IS ON OR OFF
def start(self,):
    machineSignalInputPin = self.machineSignalInputPin
    cycleSignalInputPin = self.cycleSignalInputPin
    m30SignalInputPin = self.m30SignalInputPin
    alarmSignalInputPin = self.alarmSignalInputPin
    emergencySignalInputPin = self.emergencySignalInputPin
    spindleSignalInputPin = self.spindleSignalInputPin
    resetSignalInputPin = self.resetSignalInputPin
    runOutNotOkSignalInputPin = self.runOutNotOkSignalInputPin
    while(True):
           #object for machine on/off signal
           getCurrentSignal(self,machineSignalInputPin,"machineON","machineOFF")
           #object for cycle on/off signal
           getCurrentSignal(self,cycleSignalInputPin,"cycleON","cycleOFF")
           #object for m30 on/off signal
           getCurrentSignal(self,m30SignalInputPin,"m30ON","m30OFF")
           #object for alarm on/off signal
           getCurrentSignal(self,alarmSignalInputPin,"alarmON","alarmOFF")
           #object for emergency on/off signal
           getCurrentSignal(self,emergencySignalInputPin,"emergencyON","emergencyOFF")
           #object for spindle on/off signal
           getCurrentSignal(self,spindleSignalInputPin,"spindleON","spindleOFF")
           #object for reset on/off signal
           getCurrentSignal(self,resetSignalInputPin,"resetON","resetOFF")          
           #object for runOutNotOk on/off signal
           getCurrentSignal(self,runOutNotOkSignalInputPin,"runoutNotOkON","runoutNotOkOFF")
