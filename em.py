from pymodbus.client.sync import ModbusSerialClient 
from pymodbus.constants import Endian
import numpy as np

#create a ModbusSerialClient object
client= ModbusSerialClient(method = "rtu", port="/dev/ttyUSB0",stopbits = 1, bytesize = 8, parity = 'E', baudrate=19200)

#this function reads data from energy meter
#params : starting address of register,number of registers to read
#returns list of values which contains energy at different registers
def read_float(start_add, count):
    res = client.read_holding_registers(address=start_add,count=count, unit=1)
    val=res.registers
    d16 = np.array(val,dtype=np.int16)
    return list(d16.view(dtype = np.float32))


val = read_float(3054,24)
print(val)
client.close()