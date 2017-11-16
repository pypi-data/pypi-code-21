#!/usr/bin/env python
# -*- coding: utf-8 -*-
#     DStat Interface - An interface for the open hardware DStat potentiostat
#     Copyright (C) 2017  Michael D. M. Dryden - 
#     Wheeler Microfluidics Laboratory <http://microfluidics.utoronto.ca>
#         
#     
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#     
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#     
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
import struct
import logging
logger = logging.getLogger(__name__)

import serial

from ..errors import InputError, VarError
from ..dstat import state
from ..experiments.experiment_template import Experiment, dstat_logger

def measure_offset(time):
    gain_trim_table = [None, 'r100_trim', 'r3k_trim', 'r30k_trim', 'r300k_trim',
                        'r3M_trim', 'r30M_trim', 'r100M_trim']
    
    parameters = {}
    parameters['time'] = time
    
    gain_offset = {}
    
    for i in range(1,8):
        parameters['gain'] = i
        state.ser.start_exp(CALExp(parameters))
        logger.info("measure_offset: %s", state.ser.get_proc(block=True))
        gain_offset[gain_trim_table[i]] = state.ser.get_data(block=True)
        
    return gain_offset

class CALExp(Experiment):
    id = 'cal'
    """Offset calibration experiment"""
    def __init__(self, parameters):
        self.parameters = parameters
        self.databytes = 8
        self.scan = 0
        self.data = []

        self.commands = ["EA2 3 1 ", "EG", "ER"]

        self.commands[1] += str(self.parameters['gain'])
        self.commands[1] += " "
        self.commands[1] += "0 "
        self.commands[2] += "1 32768 "
        self.commands[2] += str(self.parameters['time'])
        self.commands[2] += " "
        self.commands[2] += "0 " # disable photodiode interlock
        
    def serial_handler(self):
        """Handles incoming serial transmissions from DStat. Returns False
        if stop button pressed and sends abort signal to instrument. Sends
        data to self.data_pipe as result of self.data_handler).
        """

        try:
            while True:
                if self.ctrl_pipe.poll():
                    input = self.ctrl_pipe.recv()
                    logger.debug("serial_handler: %s", input)
                    if input == ('a' or "DISCONNECT"):
                        self.serial.write('a')
                        logger.info("serial_handler: ABORT pressed!")
                        return False
                        
                for line in self.serial:                    
                    if self.ctrl_pipe.poll():
                        if self.ctrl_pipe.recv() == 'a':
                            self.serial.write('a')
                            logger.info("serial_handler: ABORT pressed!")
                            return False
                            
                    if line.startswith('B'):
                        self.data.append(self.data_handler(
                                        self.serial.read(size=self.databytes)))
                        
                    elif line.lstrip().startswith("#"):
                        dstat_logger.info(line.lstrip().rstrip())
                        
                    elif line.lstrip().startswith("@DONE"):
                        dstat_logger.debug(line.lstrip().rstrip())
                        self.serial.flushInput()
                        return True
                        
        except serial.SerialException:
            return False
            
    def data_handler(self, data):
        """Takes data_input as tuple -- (scan, data).
        Returns:
        current
        """
        
        seconds, milliseconds, current = struct.unpack('<HHl', data)
        return current
    
    def data_postprocessing(self):
        """Averages data points
        """
        
        sum = 0
        self.data[0] = 0 # Skip first point
        
        for i in self.data:
            sum += i
        
        sum /= len(self.data)
        
        if (sum > 32767):
            sum = 32767
        elif (sum < -32768):
            sum = -32768
        
        self.data_pipe.send(sum)        