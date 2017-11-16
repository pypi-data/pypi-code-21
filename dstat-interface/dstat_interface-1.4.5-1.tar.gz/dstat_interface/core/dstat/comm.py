#!/usr/bin/env python
#     DStat Interface - An interface for the open hardware DStat potentiostat
#     Copyright (C) 2014  Michael D. M. Dryden - 
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
import multiprocessing as mp
from collections import OrderedDict
import logging

from pkg_resources import parse_version
try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GObject
except ImportError:
    print "ERR: GTK not available"
    sys.exit(1)
import serial
from serial.tools import list_ports

from ..errors import InputError, VarError

logger = logging.getLogger(__name__)
dstat_logger = logging.getLogger("{}.DSTAT".format(__name__))
exp_logger = logging.getLogger("{}.Experiment".format(__name__))

from . import state

class AlreadyConnectedError(Exception):
    def __init__(self):
        super(AlreadyConnectedError, self).__init__(self,
            "Serial instance already connected.")

class NotConnectedError(Exception):
    def __init__(self):
        super(NotConnectedError, self).__init__(self,
            "Serial instance not connected.")
            
class ConnectionError(Exception):
    def __init__(self):
        super(ConnectionError, self).__init__(self,
            "Could not connect.")

class TransmitError(Exception):
    def __init__(self):
        super(TransmitError, self).__init__(self,
            "No reply received.")

def _serial_process(ser_port, proc_pipe, ctrl_pipe, data_pipe):
    ser_logger = logging.getLogger("{}._serial_process".format(__name__))
    connected = False
    
    
    for i in range(5):
        time.sleep(1) # Give OS time to enumerate
    
        try:
            ser = serial.Serial(ser_port, timeout=1)
            ser_logger.info("Connecting")
            time.sleep(.5)
            connected = True
        except serial.SerialException:
            pass
        
        if connected is True:
            break
    
    try:
        if ser.isOpen() is False:
            ser_logger.info("Connection Error")
            proc_pipe.send("SERIAL_ERROR")
            return 1
    except UnboundLocalError:  # ser doesn't exist
        ser_logger.info("Connection Error")
        proc_pipe.send("SERIAL_ERROR")
        return 1
        
    ser.write('!0 ')
    
    for i in range(10):
        if ser.readline().rstrip()=="@ACK 0":
            if ser.readline().rstrip()=="@RCV 0":
                break
        else:
            time.sleep(.5)
            ser.reset_input_buffer()
            ser.write('!0 ')
            time.sleep(.1)

    while True:
        # These can only be called when no experiment is running
        if ctrl_pipe.poll(): 
            ctrl_buffer = ctrl_pipe.recv()
            if ctrl_buffer in ('a', "DISCONNECT"):
                proc_pipe.send("ABORT")
                try:
                    ser.write('a')
                except serial.SerialException:
                    return 0
                ser_logger.info("ABORT")
                
                if ctrl_buffer == "DISCONNECT":
                    ser_logger.info("DISCONNECT")
                    ser.rts = False
                    ser._update_dtr_state()  # Need DTR update on Windows
                    
                    ser.close()
                    proc_pipe.send("DISCONNECT")
                    return 0
            
        elif proc_pipe.poll():
            while ctrl_pipe.poll():
                ctrl_pipe.recv()
            try:
                return_code = proc_pipe.recv().run(ser, ctrl_pipe, data_pipe)
            except serial.SerialException:
                proc_pipe.send("DISCONNECT")
                ser.rts = False
                ser._update_dtr_state()  # Need DTR update on Windows
                ser.close()
                return 0
            ser_logger.info('Return code: %s', str(return_code))

            proc_pipe.send(return_code)
        
        else:
            time.sleep(.1)
            


class SerialConnection(GObject.Object):
    __gsignals__ = {
        'connected': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'disconnected': (GObject.SIGNAL_RUN_FIRST, None, ())
    }
    
    def __init__(self):
        super(SerialConnection, self).__init__()
        self.connected = False
    
    def connect(self, ser_port):
        if self.connected is False:
            self.proc_pipe_p, self.proc_pipe_c = mp.Pipe(duplex=True)
            self.ctrl_pipe_p, self.ctrl_pipe_c = mp.Pipe(duplex=True)
            self.data_pipe_p, self.data_pipe_c = mp.Pipe(duplex=True)
    
            self.proc = mp.Process(target=_serial_process, args=(ser_port,
                                    self.proc_pipe_c, self.ctrl_pipe_c,
                                    self.data_pipe_c))
            self.proc.start()
            time.sleep(2)
            if self.proc.is_alive() is False:
                raise ConnectionError()
                return False
            self.connected = True
            self.emit('connected')
            return True
        else:
            raise AlreadyConnectedError()
            return False
    
    def assert_connected(self):
        if self.connected is False:
            raise NotConnectedError()
    
    def start_exp(self, exp):
        self.assert_connected()
        
        self.proc_pipe_p.send(exp)
    
    def stop_exp(self):
        self.assert_connected()
        self.send_ctrl('a')
        
    def get_proc(self, block=False):
        self.assert_connected()
            
        if block is True:
            return self.proc_pipe_p.recv()
        else:
            if self.proc_pipe_p.poll() is True:
                return self.proc_pipe_p.recv()
            else:
                return None
                
    def get_data(self, block=False):
        self.assert_connected()
        
        if block is True:
            return self.data_pipe_p.recv()
        else:
            if self.data_pipe_p.poll() is True:
                return self.data_pipe_p.recv()
            else:
                return None
    
    def flush_data(self):
        self.assert_connected()
        
        while self.data_pipe_p.poll() is True:
            self.data_pipe_p.recv()
    
    def send_ctrl(self, ctrl):
        self.assert_connected()
        
        self.ctrl_pipe_p.send(ctrl)
    
    def disconnect(self):
        logger.info("Disconnecting")
        self.send_ctrl('DISCONNECT')
        self.proc.join()
        self.emit('disconnected')
        self.connected = False

class VersionCheck(object):
    def __init__(self):
        pass
        
    def run(self, ser, ctrl_pipe, data_pipe):
        """Tries to contact DStat and get version. Returns a tuple of
        (major, minor). If no response, returns empty tuple.
            
        Arguments:
        ser_port -- address of serial port to use
        """
        try:
            ser.reset_input_buffer()
            ser.write('!1\n')
    
            for i in range(10):
                if ser.readline().rstrip()=="@ACK 1":
                    ser.write('V\n')
                    if ser.readline().rstrip()=="@RCV 1":
                        break
                else:
                    time.sleep(.5)
                    ser.reset_input_buffer()
                    ser.write('!1\n')
                    time.sleep(.1)
                    
            for line in ser:
                dstat_logger.info(line)
                if line.startswith('V'):
                    input = line.lstrip('V')
                elif line.startswith("#"):
                    dstat_logger.info(line.lstrip().rstrip())
                elif line.lstrip().startswith("@DONE"):
                    dstat_logger.debug(line.lstrip().rstrip())
                    ser.reset_input_buffer()
                    break
                    
            pcb, sep, firmware = input.strip().rpartition('-')
            
            if pcb == "":
                pcb = firmware
                firmware = False
                logger.info("Your firmware does not support version detection.")
                
                data_pipe.send((pcb, False))
                
            else:
                logger.info(
                    "Firmware Version: {}".format(
                        hex(int(firmware)).lstrip('0x')
                    )
                )
                data_pipe.send((
                                pcb,
                                hex(int(firmware)).lstrip('0x')
                                ))
            
            logger.info(
                "PCB Version: {}".format(pcb)
            )

            status = "DONE"
        
        except UnboundLocalError as e:
            status = "SERIAL_ERROR"
        except SerialException as e:
            logger.error('SerialException: %s', e)
            status = "SERIAL_ERROR"
        finally:
            return status

def version_check(ser_port):
    """Tries to contact DStat and get version. Stores version in state.
    If no response, returns False, otherwise True.
        
    Arguments:
    ser_port -- address of serial port to use
    """    
    state.ser = SerialConnection()
    
    state.ser.connect(ser_port)
    state.ser.start_exp(VersionCheck())
    result = state.ser.get_proc(block=True)
    if result == "SERIAL_ERROR":
        state.dstat_version = None
        state.firmware_version = None
        return False
    else:
        buffer = state.ser.get_data(block=True)
    version, state.firmware_version = buffer
    state.dstat_version = parse_version(version)
    logger.debug("version_check done")
    time.sleep(.1)
    
    return True

class Settings(object):
    def __init__(self, task, settings=None):
        self.task = task
        self.settings = settings
        
    def run(self, ser, ctrl_pipe, data_pipe):
        """Tries to contact DStat and get settings. Returns dict of
        settings.
        """
        
        self.ser = ser
        
        if 'w' in self.task:
            self.write()
            
        if 'r' in self.task:
            data_pipe.send(self.read())
        
        status = "DONE"
        
        return status
        
    def read(self):
        settings = OrderedDict()
        self.ser.reset_input_buffer()
        self.ser.write('!2\n')

        for i in range(10):
            if self.ser.readline().rstrip()=="@ACK 2":
                self.ser.write('SR\n')
                if self.ser.readline().rstrip()=="@RCV 2":
                    break
            else:
                time.sleep(.5)
                self.ser.reset_input_buffer()
                self.ser.write('!2\n')
                time.sleep(.1)
                
        for line in self.ser:
            if line.lstrip().startswith('S'):
                input = line.lstrip().lstrip('S')
            elif line.lstrip().startswith("#"):
                dstat_logger.info(line.lstrip().rstrip())
            elif line.lstrip().startswith("@DONE"):
                dstat_logger.debug(line.lstrip().rstrip())
                self.ser.reset_input_buffer()
                break
            
        parted = input.rstrip().split(':')
        
        for i in range(len(parted)):
            settings[parted[i].split('.')[0]] = [i, parted[i].split('.')[1]]

        return settings
        
    def write_command(self, cmd, params=None, retry=5):
        """Write command to serial with optional number of retries."""
        def get_reply(retries = 3):
            while True:
                reply = self.ser.readline().rstrip()
                if reply.startswith('#'):
                    dstat_logger.info(reply)
                elif reply == "":
                    retries -= 1
                    if retries <= 0:
                        raise TransmitError
                else:
                    return reply
        
        n = len(cmd)
        if params is not None:
            n_params = len(params)
            
        for _ in range(retry):
            tries = 5
            while True:
                time.sleep(0.2)
                self.ser.reset_input_buffer()
                self.ser.write('!{}\n'.format(n))
                time.sleep(.1)
                
                try:
                    reply = get_reply()
                except TransmitError:
                    if tries <= 0:
                        continue
                    tries -= 1
                    pass
                else:
                    break
        
            if reply != "@ACK {}".format(n):
                logger.warning("Expected ACK got: {}".format(reply))
                continue
            
            tries = 5
            
            while True:
                self.ser.write('{}\n'.format(cmd))
                try:
                    reply = get_reply()
                except TransmitError:
                    if tries <= 0:
                        continue
                    tries -= 1
                    pass
                else:
                    break
        
            if reply != "@RCV {}".format(n):
                logger.warning("Expected RCV got: {}".format(reply))
                continue

            if params is None:
                return True
            
            tries = 5
            
            while True:
                try:
                    reply = get_reply()
                except TransmitError:
                    if tries <= 0:
                        continue
                    tries -= 1
                    pass
                else:
                    break
                
            if reply != "@RQP {}".format(n_params):
                logger.warning("Expected RQP got: {}".format(reply))
                continue
            
            tries = 5
            
            for i in params:
                while True:
                    self.ser.write(i + " ")
                    try:
                        reply = get_reply()
                        if reply == "@RCVC {}".format(i):
                            break
                    except TransmitError:
                        if tries <= 0:
                            continue
                        tries -= 1
                        pass
                    else:
                        break
            return True
        return False
        
    def write(self):
        write_buffer = range(len(self.settings))
        
        for i in self.settings: # make sure settings are in right order
            write_buffer[self.settings[i][0]] = self.settings[i][1]
        
        to_write = " ".join(write_buffer) + " "
        n = len(to_write)
        logger.debug("to_write = %s", to_write)
        
        if not self.write_command('SW' + to_write):
            logger.error("Could not write command.")
        
def read_settings():
    """Tries to contact DStat and get settings. Returns dict of
    settings.
    """
    
    state.ser.flush_data()
    state.ser.start_exp(Settings(task='r'))
    state.settings = state.ser.get_data(block=True)

    logger.info("Read settings from DStat")
    logger.debug("read_settings: %s", state.ser.get_proc(block=True))
    
    return
    
def write_settings():
    """Tries to write settings to DStat from global settings var.
    """
    
    logger.debug("Settings to write: %s", state.settings)
    
    state.ser.flush_data()
    state.ser.start_exp(Settings(task='w', settings=state.settings))
    logger.info("Wrote settings to DStat")
    logger.debug("write_settings: %s", state.ser.get_proc(block=True))
    
    return
    
class LightSensor:
    def __init__(self):
        pass
        
    def run(self, ser, ctrl_pipe, data_pipe):
        """Tries to contact DStat and get light sensor reading. Returns uint of
        light sensor clear channel.
        """
        
        ser.reset_input_buffer()
        ser.write('!')
                
        while not ser.read()=="@":
            self.ser.reset_input_buffer()
            ser.write('!')
            
        ser.write('T')
        for line in ser:
            if line.lstrip().startswith('T'):
                input = line.lstrip().lstrip('T')
            elif line.lstrip().startswith("#"):
                dstat_logger.info(line.lstrip().rstrip())
            elif line.lstrip().startswith("@DONE"):
                dstat_logger.debug(line.lstrip().rstrip())
                ser.reset_input_buffer()
                break
                
        parted = input.rstrip().split('.')
        
        data_pipe.send(parted[0])
        status = "DONE"
        
        return status

def read_light_sensor():
    """Tries to contact DStat and get light sensor reading. Returns uint of
    light sensor clear channel.
    """
    
    state.ser.flush_data()
    state.ser.start_exp(LightSensor())
    
    logger.debug("read_light_sensor: %s", state.ser.get_proc(block=True))
    
    return state.ser.get_data(block=True)

class SerialDevices(object):
    """Retrieves and stores list of serial devices in self.ports"""
    def __init__(self):
        self.ports = []
        self.refresh()
    
    def refresh(self):
        """Refreshes list of ports."""
        try:
            self.ports, _, _ = zip(*list_ports.grep("DSTAT"))
        except ValueError:
            self.ports = []
            logger.error("No serial ports found")