# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 16:28:12 2017

@author: Sharada
"""

import numpy as np
from time import sleep
from . import osensaimos

#shows pitch, roll, yaw angle 

# see p. 23 of P Rizun's PhD thesis

def setup(portname, baudrate):
    global imos
    imos = osensaimos.IMOS(portname, baudrate, timeout=1)
    print(imos.dictionary())

def orthonormalize(g, m):
    k = g / np.linalg.norm(g)
    i = np.cross(m,k) / np.linalg.norm( np.cross(m,k) )
    j = np.cross(k,i)
    return np.array([i,j,k])


# see p. 163 of P Rizun's PhD thesis

def yaw(R):
    return np.arctan2(-R[0,1],R[1,1]) 

def pitch(R):
    return np.arctan2(R[2,1],np.sqrt(R[1,0]*R[1,0]+R[1,1]*R[1,1])) 

def roll(R):
    return np.arctan2(-R[2,0],R[2,2]) 

def read_angles(imos, measurement1, measurement2):
    try:
        #imos = osensaimos.IMOS("COM6",115200,timeout=1)
        #d = imos.dictionary()
        #print(d)
        accel_array_avg = np.asarray([0,0,0])
        magn_array_avg = np.asarray([0,0,0])
        while True:
            accel_reading = imos.read(measurement1)
            magn_reading = imos.read(measurement2)
            accel_array = np.asarray(accel_reading)
            magn_array = np.asarray(magn_reading)
            accel_array_avg = accel_array_avg + 0.25*(accel_array - accel_array_avg)
            magn_array_avg = magn_array_avg + 0.25*(magn_array - magn_array_avg)
            matrix = orthonormalize(accel_array_avg, magn_array_avg)
            pitchVal = np.degrees(pitch(matrix))
            rollVal = np.degrees(roll(matrix))
            yawVal = np.degrees(yaw(matrix))
            print("{:0.2f}\t {:0.2f}\t {:0.2f}".format(pitchVal, rollVal, yawVal))
            
    except Exception as e:
        if imos is not None:
            print("Couldn't connect")
            imos.disconnect()
            print(e)
    except KeyboardInterrupt:
        #if imos is not None:
            #print("Exiting angles test")
            #imos.disconnect()
        pass
    
    
