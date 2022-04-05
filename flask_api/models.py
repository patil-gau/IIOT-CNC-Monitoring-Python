from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

#signal table 
class signals(db.Model):
    id = db.Column(db.INT, primary_key=True)
    machineId = db.Column(db.String)
    process = db.Column(db.String)
    timeStamp = db.Column(db.String)

#pins table
class pinout(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    signalName = db.Column(db.String)
    pinNumber = db.Column(db.INTEGER)
    status = db.Column(db.String)

#production table
class production(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    emp_id = db.Column(db.String)
    operatorName = db.Column(db.String)
    jobId = db.Column(db.String)
    shift = db.Column(db.String)
    component = db.Column(db.String)
    modelName = db.Column(db.String)
    operation = db.Column(db.String)
    cycleTime = db.Column(db.String)
    inspectionStatus = db.Column(db.INTEGER)
    status = db.Column(db.INTEGER)
    timeStamp = db.Column(db.String)
    machineId = db.Column(db.String)
    date = db.Column(db.String)
    progress=db.Column(db.String)

#liveStatus table
class liveStatus(db.Model):
    id = db.Column(db.INT, primary_key=True)
    machineId = db.Column(db.String)
    machineType = db.Column(db.String)
    status = db.Column(db.String)
    color = db.Column(db.String)
    signalName = db.Column(db.String)

#ShiftData table
class ShiftData(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    shift = db.Column(db.String)
    fromTime = db.Column(db.String)
    toTime = db.Column(db.String)

#Alarm table
class alarm(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    machineId = db.Column(db.String)
    operatorName = db.Column(db.String)
    jobId = db.Column(db.String)
    shift = db.Column(db.String)
    component = db.Column(db.String)
    modelName = db.Column(db.String)
    operation = db.Column(db.String)
    timeStamp = db.Column(db.String)
    reason = db.Column(db.String)
    errorCode = db.Column(db.String)

#idleTimeout Table
class idleTimeout(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    emp_id = db.Column(db.String)
    machineId = db.Column(db.String)
    operatorName = db.Column(db.String)
    shift = db.Column(db.String)
    component = db.Column(db.String)
    modelName = db.Column(db.String)
    operation = db.Column(db.String)
    timeStamp = db.Column(db.String)
    reason = db.Column(db.String)
    jobId = db.Column(db.String)

#energyMeter table
class energyMeter(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    voltage1 = db.Column(db.String)
    voltage2 = db.Column(db.String)
    voltage3 = db.Column(db.String)
    voltage1 = db.Column(db.String)
    current1 = db.Column(db.String)
    current2 = db.Column(db.String)
    current3 = db.Column(db.String)
    power = db.Column(db.String)
    energy = db.Column(db.String)

#serverConfiguration table
class serverConf(db.Model):
    id = db.Column(db.INT, primary_key=True)
    ip = db.Column(db.String)

#Network Details Table
class networkConf(db.Model):
    id = db.Column(db.INT, primary_key=True)
    ip = db.Column(db.String)
    gateway = db.Column(db.String)
    dns = db.Column(db.String)

#Other Settings for Admin 
class otherSettings(db.Model):
    id = db.Column(db.INT, primary_key=True)
    machineId = db.Column(db.String)
    batchSize = db.Column(db.String)
    holdingRelay = db.Column(db.String)
    machineBypass = db.Column(db.String)
    cleaningInterval = db.Column(db.String)
    idleTimeout = db.Column(db.String)
    machineType = db.Column(db.String)

class Maintenance(db.Model): 
    id = db.Column(db.Integer,primary_key=True)
    machineId = db.Column(db.String)
    operator_id = db.Column(db.String) 
    time_stamp = db.Column(db.String)
    reason = db.Column(db.String, max_length=100)  
