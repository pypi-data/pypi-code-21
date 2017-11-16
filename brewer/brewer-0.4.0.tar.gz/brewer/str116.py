#!/usr/bin/env python
import serial
from . import settings
import time
import binascii
import os

def _write_message(data):
    try:
        usart = serial.Serial (settings.port,settings.baudRate)
    except IOError as e :
        print(("Failed to create serial object. ({})".format(e)))

    usart.timeout = settings.timeout
    message_bytes = data.decode("hex")
    try:
        usart.write(message_bytes)
        if settings.DEBUG:
            print('success')
    except IOError as e :
        print(("Failed to write to the port. ({})".format(e)))

def _write_message_with_response(data):
    usart = serial.Serial (settings.port,settings.baudRate)
    usart.timeout = settings.timeout
    message_bytes = data.decode("hex")
    try:
        usart.write(message_bytes)
        #print usart.open  # True for opened
        if usart.open:
            time.sleep(0.02)
            size = usart.inWaiting()
            if size:
                data = usart.read(size)
                # print binascii.hexlify(data)
            else:
                print('no data')
        else:
            print('usart not open')
    except IOError as e :
        print(("Failed to write to the port. ({})".format(e)))
    return binascii.hexlify(data)

def _get_checksum(data):
    checksum = sum(bytearray.fromhex(data))
    checksumstripped = hex(checksum).replace('0x', '')
    return checksumstripped.zfill(2)

def set_relay(relaynumber, onoff):
    #command to turn on relay is 0x08 0x17
    #format is
    #MA0, MA1, 0x08, 0x17, CN, start number output (relaynumber), \
    #number of outputs (usually 0x01), 00/01 (off/on), CS (calculated), MAE
    #need to do a checksum on 0x08, 0x17, CN, relaynumber, 0x01, 0x01
    relaynumberhex = hex(relaynumber).replace('0x', '').zfill(2)
    str_to_checksum = '0817' + settings.CN + str(relaynumberhex) \
        + '01' + str(onoff).zfill(2)
    CS = _get_checksum(str_to_checksum)
    bytestring = settings.MA0 + settings.MA1 + str_to_checksum \
        + str(CS) + settings.MAE
    if settings.DEBUG:
        print(('set_relay bytestring: ' + bytestring))
    _write_message(bytestring)

def get_relay(relaynumber):
    '''Get the status of the requested relay (true/false)'''
    time.sleep(0.005)
    str_to_checksum = '0714' + settings.CN + '0010'
    CS = _get_checksum(str_to_checksum)
    bytestring = settings.MA0 + settings.MA1 + str_to_checksum \
        + str(CS) + settings.MAE
    relaystatus = _write_message_with_response(bytestring)[6:-4]
    test = relaystatus[relaynumber*2:relaynumber*2+2]
    if int(test) > 0:
        return True
    else:
        return False
def get_relays_status():
    #command to get the status of all of the relays in an array.
    #format is
    #MA0, MA1, 0x07, 0x14, CN, start number output, number of outputs, CS, MAE
    #returns
    #SL0, SL1, BC, output first, output next,..., CS, SLE
    str_to_checksum = '0714' + settings.CN + '0010'
    CS = _get_checksum(str_to_checksum)
    bytestring = settings.MA0 + settings.MA1 + str_to_checksum \
        + str(CS) + settings.MAE
    print(('relay status bytestring: ' + bytestring))
    relaystatus = _write_message_with_response(bytestring)[6:-4]
    print(('relay status: ' + relaystatus))


    totalrelays = len(relaystatus)
    n = 0
    while(n < totalrelays):
        if str(relaystatus[n:n+2]) == '00':
            print(('relay ' + str(n/2).zfill(2) + ': off'))
        else:
            print(('relay ' + str(n/2).zfill(2) + ': on'))
        n += 2



def set_baudrate():
    """
    This function changes the baudrate on the str116 controller card.
    IMPORTANT! if you change the baudrate using this function, you MUST
    update the baudrate listed in the settings file, or your communications
    will not work. This is mainly a setup function that can be used to
    initialize the controller.
    """
    #usart = serial.Serial (settings.port,settings.baudRate) #current settings
    d = {'300':0,'600':1,'1200':2,'2400':3,'4800':4,'9600':5,'19200':6, \
        '38400':7,'57600':8,'115200':9}
    print(d)
    bytestring = "55AA083302AA55064277" #set baudrate to 19200
    print(bytestring)
    #message_bytes = bytestring.decode("hex")
    #usart.write(message_bytes)
