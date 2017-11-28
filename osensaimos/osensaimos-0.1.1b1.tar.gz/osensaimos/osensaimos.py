"""
OsensaIMOS: A Python module for interfacing with OSENSA IMOS

Created on Fri Nov 24 16:28:12 2017

@author: Sharada Balaji, Caleb Ng
"""

__author__   = 'Sharada Balaji, Caleb Ng'
__url__      = 'https://github.com/osensa/osensaimos'
__license__  = 'MIT License'

__version__  = '0.1.0'
__status__   = 'Beta'

import sys
import glob
import serial
import json
import time
from struct import *
from minimalmodbusosensa import Instrument, SecurityError

#5 second timeout for some commands
class TimeoutError(Exception):
    def __init__(self, value = "Timed out"):
        self.value = value
        
    def __str__(self):
        return repr(self.value)
    

class InvalidSetupError(Exception):
    pass

"""
DEFAULT SETTINGS:
    baudrate            = 9600
    # of databits       = 8
    parity              = NONE
    stop bits           = 1
"""
SLAVEADDRESS = 1
BAUDRATE = 115200
NUMBITS = serial.EIGHTBITS
PARITY = serial.PARITY_NONE
STOP = serial.STOPBITS_ONE
PY3K = sys.version_info >= (3,0)

def serial_get_portlist():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    portlist = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            portlist.append(port)
            print(port)
        except (OSError, serial.SerialException):
            pass
    return portlist


def bits_to_float(bytevalue):
    s = pack('I', bytevalue)
    return unpack('f', s)[0]

def parse_float(register_values, endian='BIG'):
    if (endian == 'BIG'):
        reg1shift = 16
        reg0shift = 0
    else:
        reg1shift = 0
        reg0shift = 16
    if (len(register_values) < 0):
        value = 0
    elif (len(register_values) == 1):
        value = register_values[0] << reg0shift
    else:
        value = (register_values[1] << reg1shift) | (register_values[0] << reg0shift)
    # print(value)
    return bits_to_float(value)


class IMOS():
    """
    Transmitter class for talking to IMOS sensors

    Args:
        * param1: 
        * param2:

    """
    
    #set up sensor object
    def __init__(self, port, baudrate, timeout=1):
        self.modbus = Instrument(port, SLAVEADDRESS)
        self.modbus.serial.parity = PARITY
        self.modbus.serial.baudrate = baudrate
        self.modbus.serial.timeout = timeout
        # self.modbus.close_port_after_each_call = False
    
    #change the baudrate once you have connected at the current baudrate 
    def set_baudrate(self, baudrate):
        rate = self.baudrate_check(baudrate)
        print(rate)
        self.modbus_write(0,rate)
    
    #making baudrate values conform to what the register values should be
    def baudrate_check(self, baudrate):
        if baudrate == 1200:
            rate = 0x0001
        elif baudrate == 2400:
            rate = 0x0101
        elif baudrate == 4800:
            rate = 0x0201
        elif baudrate == 9600:
            rate = 0x0301
        elif baudrate == 19200:
            rate = 0x0401
        elif baudrate == 38400:
            rate = 0x0501
        elif baudrate == 57600:
            rate = 0x0601
        elif baudrate == 115200:
            rate = 0x0701
        elif baudrate == 230400:
            rate = 0x0801
        elif baudrate == 460800:
            rate = 0x0901
        elif baudrate == 921600:
            rate = 0x1001
        else:
            rate = 701
        return rate 
    
    #disconnect from the IMOS sensor
    def disconnect(self):
        self.modbus.serial.close()
    
    #read any value by naming it, can read calibrated and uncalibrated values
    def read(self, key, calibrated=True, JSON=False):
        serialization = self.main_dictionary[key]['serialization']
        if calibrated:
            address = self.main_dictionary[key]['address']
        else:
            key = "$" + key
            address = self.main_dictionary[key]['address']
        return unpack(serialization, self.modbus_read(address, calcsize(serialization)))
    
    #this checks for timeouts
    def timeoutChecker(self, startTime, currTime, timeout=5):
        if (currTime - startTime) >= timeout:
            raise TimeoutError
        
    #set up the dictionary before trying to use it in later functions
    def dictionary(self, printStream=False):
        self.modbus.custom_command(0x01, 0x00)
        rxbytes = bytearray()
        try:
            startTime = time.time()
            while True:
                bytes_to_read = self.modbus.serial.inWaiting() #shows number of bytes to receive
                if (bytes_to_read == 0):
                    self.timeoutChecker(startTime, time.time())
                if (bytes_to_read > 0):
                    response = self.modbus.serial.read(bytes_to_read) #reads the bytes
                    if (0 in response):
                        # Remove null character from string
                        temp = list(response)
                        temp.remove(0)
                        response = bytes(temp)
                        # Append response to string and exit loop
                        rxbytes.extend(response)
                        break
                    else:
                        rxbytes.extend(response)
        except KeyboardInterrupt:
            return 0
        if (printStream):
            text = ''
            if not PY3K:
                for elem in rxbytes:
                    text += elem
            else:
                for elem in rxbytes.decode('cp437'):
                    text += elem
            print(text)
        self.main_dictionary = json.loads(rxbytes)
        return self.main_dictionary

    #gives the list of possible measurements
    def measurements(self):
        # Update internal dictionary
        self.dictionary()
        # Create subset with just measurement type keys
        subdict = dict()
        for key in self.main_dictionary.keys():
            datatype = self.main_dictionary[key]['type']
            if (datatype == 'measurement'):
                subdict[key] = self.main_dictionary[key]
        # Return sub dictionary
        return subdict       

    #gives the list of possible calibration coefficients for each sensor
    def coefficients(self):
        # Update internal dictionary
        self.dictionary()
        # Create subset with just measurement type keys
        subdict = dict()
        for key in self.main_dictionary.keys():
            datatype = self.main_dictionary[key]['type']
            if (datatype == 'calibration_coefficient'):
                subdict[key] = self.main_dictionary[key]
        # Return sub dictionary
        return subdict   
    
    #sets up streaming rate and which measurements to stream. Can take multiple measurement args.
    def setup_stream(self, streamRate, *arg):
        print("number of args",len(arg))
        rate = self.streamRateCheck(streamRate)
        print("stream rate is", rate)
        address = main_dictionary['stream_data']['address']
        for a in arg:
            print(a)
            targetAddress = self.dictionary[a]['address']
            for i in range(0,6):
                self.modbus_write_val(address, targetAddress, 'H') #write target register address to streaming register
                address += 1
                targetAddress += 1            
        self.modbus_write(main_dictionary['stream_rate']['address'], rate) #set the streaming rate based on config table
        n_registers = len(arg) * 6
        self.modbus_write_val(main_dictionary['num_to_stream']['address'], n_registers, 'H') #set how many registers to stream
        
        
    #converting streaming rate in Hz to the right code and catching values in between
    def streamRateCheck(self, streamRate):
        if (streamRate == 100):
            streamRate = 0x0000
        if streamRate == 200:
            streamRate = 0x0001
        if streamRate == 400:
            streamRate = 0x0002
        if streamRate == 800:
            streamRate = 0x0003
        else:
            streamRate = 0x0000 #default is 100Hz
        return streamRate
    
    
    #starts streaming, results will be based on the setup function
    def start_stream(self, serial_hold=False):
        self.modbus.custom_command(0x00, 0x01)
        if (not serial_hold):
            return
        try:
            startTime = time.time()
            while True:
                bytes_to_read = self.modbus.serial.inWaiting()
                if (bytes_to_read == 0):
                    self.timeoutChecker(startTime, time.time())
                if (bytes_to_read > 0):
                    response = self.modbus.serial.read(bytes_to_read)
                    # Print response
                    print(str(response))
        except KeyboardInterrupt:
            self.stop_stream()
    
    #sets the device to streaming mode
    def modbus_start_stream(self):
        self.modbus.custom_command(0x00, 0x01)
    
    #stop streaming
    def stop_stream(self):
        self.modbus.custom_command(0x00, 0x00)
        rxbytes = bytearray()
        try:
            while True:
                startTime = time.time()
                bytes_to_read = self.modbus.serial.inWaiting()
                if (bytes_to_read > 0):
                    response = self.modbus.serial.read(bytes_to_read)
                    if (bytes_to_read == 0):
                        self.timeoutChecker(startTime, time.time())
                    if (0 in response):
                        # Remove null character from string
                        temp = list(response)
                        temp.remove(0)
                        response = bytes(temp)
                        # Append response to string and exit loop
                        rxbytes.extend(response)                        
                        text = ''
                        for elem in rxbytes.decode():
                            text += elem
                        print(text)
                        break
                    else:
                        rxbytes.extend(response)
        except KeyboardInterrupt:
            pass
    
    #modbus command to stop streaming 
    def modbus_stop_stream(self):
        self.modbus.custom_command(0x00, 0x00)
    
    #modbus for reading the number of bytes you want
    def modbus_read(self, address, n_bytes): #2 addresses are 4 bytes which is 2 registers
        # Get # of registers (each register is 16-bits which is 2-bytes)
        n_registers = n_bytes/2
        bytearr = bytearray()
        # Read register values
        values = self.modbus.read_registers(address, int(n_registers))
        # Reconstruct byte array
        for elem in values: 
            bytearr.append(0x00FF & elem)
            bytearr.append((0xFF00 & elem) >> 8)
        # Return read bytes
        return bytearr 
    
    #gives the serialization format of a sensor
    def get_serialization(self, key, calibrated=True, JSON=False):
        serialization = self.main_dictionary[key]['serialization']
        return serialization 
    
    #writes a value (proper number) to the given address based on serialization format
    def modbus_write_val(self, address, value, serialization): #takes a value to write
        n_registers = int(calcsize(serialization)/2) #number of registers to writee to
        compartments = [None]*n_registers #a containter for the value
        modValue = pack(serialization,value) #convert the value to the correct serialization in bytes
        #now modify the bytes so the input format is right 
        i = 0
        j = 0
        #this feels like it shouldn't work but it does.
        while i <= n_registers:
            (compartments[j],) = unpack('H',modValue[i:i+2]) #separate the bytes into registers and put them into the 0-65536 range
            i += 2
            j += 1
        try:
            self.modbus.write_registers(address,compartments)
        except IOError:
            print('IOError occurred while writing...')
        except ValueError:
            print('ValueError occurred while writing...')
 
           
     #modbus command to write a byte to a given address       
    def modbus_write(self, address, byteToWrite):
        try:
            self.modbus.write_register(address, byteToWrite)
        except IOError:
            print('IOError occurred while writing...')
        except ValueError:
            print('ValueError occurred while writing...')
 
    
    #load calibration coefficients, calTable is a dictionary        
    def load_calibration(self, calTable, savetoFlash=True):
        print(calTable.keys())
        #print(calTable.values())
        c = self.coefficients()
        for key in calTable.keys():
            #get the address for gamma and beta values of that sensor, then write the coefficient values to memory
            gammaKey = key + "_gamma"
            gammaAddress = c[gammaKey]['address']
            betaKey = key + "_beta"
            betaAddress = c[betaKey]['address']
            for i in range(0,9):
                gammaToWrite = calTable[key]['gamma'][i]
                gammaSerialization = self.get_serialization(gammaKey)[i]
                self.modbus_write_val(gammaAddress,gammaToWrite,gammaSerialization)
                gammaAddress += 2
                if (i < 3): #there are only 3 beta values
                    betaToWrite = calTable[key]['beta'][i]
                    betaSerialization = self.get_serialization(betaKey)[i]
                    self.modbus_write_val(betaAddress,betaToWrite,betaSerialization)
                    betaAddress += 2

    
    #read the calibration coefficient values
    def dump_calibration(self):
        c = self.coefficients()
        data = {} #setting up the dictionary
        for key in c.keys():
            address = c[key]['address']
            serialization = self.get_serialization(key)
            value = unpack(serialization, self.modbus_read(address,calcsize(serialization)))
            data[key] = value
        return data #data is already a dictionary with key-value pairs where you can access elements by name
    
    def crc_table_init(self):
        # Initialize crc_table
        self.crc_table = list(range(256))
    #	print('crc table before: {}'.format(crc_table))
        for i in range(0,256):
            crc = 0
            c = i
            for j in range(0, 8):
                if ((crc ^ c) & 0x0001):
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc = crc >> 1
                c = c >> 1
            self.crc_table[i] = crc
    #	print('crc table after: {}'.format(crc_table))

    def update_crc(self, crc, c):
        int_c = 0x00ff & c
        if (self.crc_table is None):
            # Initialize table
            self.crc_table_init()
        tmp = crc ^ int_c
        crc = (crc >> 8) ^ self.crc_table[tmp & 0xff]
        return crc