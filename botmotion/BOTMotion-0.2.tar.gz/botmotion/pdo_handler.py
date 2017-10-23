# BOT Motion Module
#
# PDO Handler
#
# Author:      Henrik Stroetgen <hstroetgen@synapticon.com> / <support@synapticon.com>
# Date:        2016-11-19
# Location:    Filderstadt, Germany
#
#
#
#       Copyright (c) 2016, Synapticon GmbH
#       All rights reserved.
#
#       Redistribution and use in source and binary forms, with or without
#       modification, are permitted provided that the following conditions are met:
#
#       1. Redistributions of source code must retain the above copyright notice, this
#          list of conditions and the following disclaimer.
#       2. Redistributions in binary form must reproduce the above copyright notice,
#          this list of conditions and the following disclaimer in the documentation
#          and/or other materials provided with the distribution.
#       3. Execution of this software or parts of it exclusively takes place on hardware
#          produced by Synapticon GmbH.
#
#       THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#       ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#       WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#       DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#       ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#       (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#       LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#       ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#       (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#       SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#       The views and conclusions contained in the software and documentation are those
#       of the authors and should not be interpreted as representing official policies,
#       either expressed or implied, of the Synapticon GmbH.
#

import struct
import ctypes
import time

from debug_printing import *
from pdo_constants import *
from ethernet_socket import *
from ex_thread import *

LOOP_TIME = 0.001 # sec
TIMEOUT = 5 # sec

class ExceptionWrongCMD(Exception):
    """
    Wrong command exception class
    """
    pass

class ExceptionTimeout(Exception):
    """
    PDO timeout class
    """
    pass


class Statusword_Bits(ctypes.LittleEndianStructure):
    """
    Struct for status word bits
    """
    _fields_ = [
        ('ready_to_switch_on',      ctypes.c_uint16, 1), # 0
        ('switched_on',             ctypes.c_uint16, 1), # 1
        ('operation_enabled',       ctypes.c_uint16, 1), # 2
        ('fault',                   ctypes.c_uint16, 1), # 3
        ('voltage_enabled',         ctypes.c_uint16, 1), # 4
        ('quick_stop',              ctypes.c_uint16, 1), # 5
        ('switch_on_disabled',      ctypes.c_uint16, 1), # 6
        ('warning',                 ctypes.c_uint16, 1), # 7
        ('manufacturer_specific_1', ctypes.c_uint16, 1), # 8
        ('remote',                  ctypes.c_uint16, 1), # 9
        ('target_reached',          ctypes.c_uint16, 1), # 10 CSP Target Position Ignored
        ('internal_limit_active',   ctypes.c_uint16, 1), # 11
        ('fault_over_temperature',  ctypes.c_uint16, 1), # 12
        ('operation_mode_specific', ctypes.c_uint16, 1), # 13 CSP Following Error
        ('fault_over_current',      ctypes.c_uint16, 1), # 14
        ('fault_under_voltage',     ctypes.c_uint16, 1), # 15
    ]

class Statusword_Flags(ctypes.Union):
    """
    Union for status word
    """
    _anonymous_ = ('bit',) # With this sequence, we can access the members of Statusword_Bits directly:
                           # union.ready_to_switch_on (same like union.bit.ready_to_switch_on)
    _fields_ = [
        ('bit',     Statusword_Bits), # Members of Statusword_Bits. Access every single bit of 'word' directly
        ('word',    ctypes.c_uint16)  # The statusword as uint16
    ]


class PDO_In_Struct():
    """
    Struct for incoming PDOs
    """
    def __init__(self):
        self.status_word = Statusword_Flags()
        self.operation_mode = 0

        self.position_actual = 0
        self.velocity_actual = 0
        self.torque_actual = 0

        self.secondary_position_value = 0
        self.secondary_velocity_value = 0

        self.analog_input1 = 0
        self.analog_input2 = 0
        self.analog_input3 = 0
        self.analog_input4 = 0

        self.tuning_status = 0
        self.digital_input1 = 0
        self.digital_input2 = 0
        self.digital_input3 = 0
        self.digital_input4 = 0

        self.user_miso = 0
        self.timestamp = 0


class PDO_Out_Struct():
    """
    Struct for outgoing PDOs
    """
    def __init__(self):
        self.control_word = CMD_SHUTDOWN
        self.operation_mode = OPMODE_NONE

        self.position_target = 0
        self.velocity_target = 0
        self.torque_target = 0

        self.offset_torque = 0
        self.tuning_command = 0

        self.digital_output1 = 0
        self.digital_output2 = 0
        self.digital_output3 = 0
        self.digital_output4 = 0

        self.user_mosi  = 0


class PDO_Handler(ExThread):
    """
    PDO handler. Subclasses ExThread.
    """
    def __init__(self, id, address, port):
        """
        Initialized PDO handler
        :param id: object id
        :type id: uint
        :param address: IP address
        :type address: string
        :param port: port
        :type port: uint
        """
        super(PDO_Handler, self).__init__()
        self.__id = id
        self.pdo_in = PDO_In_Struct()
        self.pdo_out = PDO_Out_Struct()

        self.__socket = EthernetSocket(self.__id, IF_NAME, address, port, 'UDP')
        self.__socket.connect()

        self.__alive = threading.Event()
        self.__alive.set()
        self.__lock = threading.Lock()
        self.__printer = DebugPrint(self.__id, 'PDO Handler')
        self.__pdo_send = False
        self.start()

    def close(self):
        """
        Close PDO thread and socket thread
        """
        self.__printer.printf('Shutdown PDO handler\n')
        self.__alive.clear()
        self.__socket.close()

    def run_with_exception(self):
        """
        PDO thread.
        Sends and receives PDOs. Reads and writes directly into structs.
        """
        timeout_time0 = 0

        while self.__alive.isSet():
            time0 = time.clock()

            msg_out = self._encode_pdo_packet()
            self.__socket.send(msg_out)

            msg_in = self.__socket.recv()
            flag_recv_msg = self._decode_pdo_packet(msg_in[0]) # msg_in is tuple of (payload, (ip, port))

            # Check for exception in socket thread
            self.__socket.check_for_exception()

            if not flag_recv_msg:
                #print 'Nothing recv'
                if timeout_time0 == 0:
                    #print 'Start timeout'
                    timeout_time0 = time.clock()
                elif (time.clock() - timeout_time0) > TIMEOUT:
                    #print 'Timeout!'
                    raise ExceptionTimeout('Timeout in PDO handler')
            else:
                timeout_time0 = 0

            time1 = time.clock()
            wait_time = LOOP_TIME - (time1 - time0)
            if wait_time < 0:
                wait_time = 0
            time.sleep(wait_time)

        self.__printer.printf('Exit PDO Thread...\n')
        

    def _decode_pdo_packet(self, data):
        """
        Decode PDO message and write into struct
        :param msg: received message
        :type msg: binary string
        :return: True, if message was not null
        :rtype: bool
        """
        if data:
            self.__lock.acquire()
            self.pdo_in.status_word.word = struct.unpack_from('H', data, 0)[0] # Struct makes a tuple. with index we get the value
            self.pdo_in.operation_mode = struct.unpack_from('b', data, 2)[0]
            self.pdo_in.position_actual = struct.unpack_from('i', data, 3)[0]
            self.pdo_in.velocity_actual = struct.unpack_from('i', data, 7)[0]
            self.pdo_in.torque_actual = struct.unpack_from('h', data, 11)[0]
            self.pdo_in.secondary_position_value = struct.unpack_from('i', data, 13)[0]
            self.pdo_in.secondary_velocity_value = struct.unpack_from('i', data, 17)[0]
            self.pdo_in.analog_input1 = struct.unpack_from('H', data, 21)[0]
            self.pdo_in.analog_input2 = struct.unpack_from('H', data, 23)[0]
            self.pdo_in.analog_input3 = struct.unpack_from('H', data, 25)[0]
            self.pdo_in.analog_input4 = struct.unpack_from('H', data, 27)[0]
            self.pdo_in.tuning_status = struct.unpack_from('I', data, 29)[0]
            self.pdo_in.digital_input4 = struct.unpack_from('B', data, 33)[0]
            self.pdo_in.digital_input4 = struct.unpack_from('B', data, 34)[0]
            self.pdo_in.digital_input4 = struct.unpack_from('B', data, 35)[0]
            self.pdo_in.digital_input4 = struct.unpack_from('B', data, 36)[0]
            self.pdo_in.user_miso = struct.unpack_from('I', data, 37)[0]
            self.pdo_in.timestamp = struct.unpack_from('I', data, 41)[0]
            self.__lock.release()
            return True
        else:
            return False

    def _encode_pdo_packet(self):
        """
        Encode PDO struct into binary message
        :return: encoded PDO struct
        :rtype: binary string
        """
        self.__lock.acquire()
        msg_out = struct.pack('<HbhiiiIBBBBI', self.pdo_out.control_word,
                           self.pdo_out.operation_mode,
                           self.pdo_out.torque_target,
                           self.pdo_out.position_target,
                           self.pdo_out.velocity_target,
                           self.pdo_out.offset_torque,
                           self.pdo_out.tuning_command,
                           self.pdo_out.digital_output1,
                           self.pdo_out.digital_output2,
                           self.pdo_out.digital_output3,
                           self.pdo_out.digital_output4,
                           self.pdo_out.user_mosi)
        self.__pdo_send = True
        self.__lock.release()
        return msg_out

    def _set_ctrl_word(self, ctrl):
        """
        Set control word
        :param ctrl: control word
        :type ctrl: uint
        """
        self.__lock.acquire()
        self.pdo_out.control_word = ctrl
        self.__lock.release()

    def _set_opmode(self, opmode):
        """
        Set operation mode
        :param opmode: operation mode
        :type opmode: uint
        """
        self.__lock.acquire()
        self.pdo_out.operation_mode = opmode
        self.__lock.release()

    def _decode_status_word(self, status_word):
        if not status_word.ready_to_switch_on and \
                not status_word.switched_on and \
                not status_word.operation_enabled and \
                not status_word.fault and \
                not status_word.switch_on_disabled:
            return 'Not ready to switch on'
        elif not status_word.ready_to_switch_on and \
                not status_word.operation_enabled and \
                not status_word.switched_on and \
                not status_word.fault and \
                    status_word.switch_on_disabled:
            return 'Switch on disabled'
        elif not status_word.switched_on and \
                not status_word.operation_enabled and \
                not status_word.fault and \
                not status_word.switch_on_disabled and \
                    status_word.quick_stop and \
                    status_word.ready_to_switch_on:
            return 'Ready to switch on'
        elif not status_word.operation_enabled and \
              not status_word.switch_on_disabled and \
              not status_word.fault and \
                  status_word.quick_stop and \
                  status_word.ready_to_switch_on and \
                  status_word.switched_on:
            return 'Switched on'
        elif not status_word.fault and \
                not status_word.switch_on_disabled and \
                status_word.ready_to_switch_on and \
                status_word.switched_on and \
                status_word.operation_enabled and \
                status_word.quick_stop:
            return 'Operation enabled'
        elif not status_word.fault and \
             not status_word.switch_on_disabled and \
             not status_word.quick_stop and \
             status_word.ready_to_switch_on and \
             status_word.switched_on and \
             status_word.operation_enabled:
            return 'Quick stop'
        elif not status_word.switch_on_disabled and \
             status_word.ready_to_switch_on and \
             status_word.switched_on and \
             status_word.operation_enabled and \
             status_word.fault:
            return 'Fault reaction active'
        elif not status_word.switch_on_disabled and \
             not status_word.ready_to_switch_on and \
             not status_word.switched_on and \
             not status_word.operation_enabled and \
             status_word.fault:
            #return 'Fault'
            if status_word.fault and \
                 status_word.fault_over_current and \
                status_word.fault_under_voltage:
                return 'Fault: Over voltage'
            elif status_word.fault and \
                 status_word.fault_over_temperature:
                return 'Fault: Over temperature'
            elif status_word.fault and \
                 status_word.fault_over_current:
                return 'Fault: Over current'
            elif status_word.fault and \
                status_word.fault_under_voltage:
                return 'Fault: Under voltage'

        else:
            return 'U shouldn\'t see me'

    def set_opmode_csp(self):
        """
        Set Cyclic synchronous position mode
        """
        #print 'Set OPMODE CSP'
        self._set_opmode(OPMODE_CSP)

    def set_opmode_csv(self):
        """
        Set Cyclic synchronous velocity mode
        """
        #print 'Set OPMODE CSV'
        self._set_opmode(OPMODE_CSV)

    def set_update_slave_pid(self):
        """
        Set user_2 PDO to 0xff. Special command to update PID parameters
        """
        self.set_user_2(0xff)

    def get_statusword(self):
        """
        Translates status word into status string
        :return: Status word as string
        :rtype: string
        """
        self.__lock.acquire()
        status_word = self.pdo_in.status_word
        self.__lock.release()
        #print 'Status word', hex(status_word.word)
        return self._decode_status_word(status_word)

    def set_position(self, pos):
        """
        Set target position into PDO struct.
        :param pos: Target position
        :type pos: int
        :exception: ExceptionWrongCMD if operation mode is not CSP
        """
        if self.pdo_out.operation_mode == OPMODE_CSP:
            while not self.__pdo_send:   # Wait until package is send
                pass
            self._set_ctrl_word(CMD_ENABLE_OP)
            self.__lock.acquire()
            self.pdo_out.position_target = pos
            self.__pdo_send = False
            self.__lock.release()
        else:
            raise ExceptionWrongCMD('Error: Set position only possible in CSP')

    def set_velocity(self, velocity):
        """
        Set target velocity into PDO struct.
        :param pos: Target velocity
        :type pos: int
        :exception: ExceptionWrongCMD if operation mode is not CSV
        """
        if self.pdo_out.operation_mode == OPMODE_CSV:
            while not self.__pdo_send:   # Wait until package is send
                pass
            self._set_ctrl_word(CMD_ENABLE_OP)
            self.__lock.acquire()
            self.pdo_out.velocity_target = velocity
            self.__pdo_send = False
            self.__lock.release()
        else:
            raise ExceptionWrongCMD('Error: Set velocity only possible in CSV')

    def set_torque(self, torque):
        """
        Set target torque into PDO struct.
        :param pos: Target torque
        :type pos: int
        :exception: ExceptionWrongCMD if operation mode is not CST
        """
        if self.pdo_out.operation_mode == OPMODE_CST:
            while not self.__pdo_send:  # Wait until package is send
                pass
            self._set_ctrl_word(CMD_ENABLE_OP)
            self.__lock.acquire()
            self.pdo_out.torque_target = torque
            self.__pdo_send = False
            self.__lock.release()
        else:
            raise ExceptionWrongCMD('Error: Set torque only possible in CST')

    def set_user_1(self, value):
        """
        Set user 1 parameter into PDO struct
        :param value: Custom value
        :type value: int
        """
        self.__lock.acquire()
        self.pdo_out.user_1 = value
        self.__lock.release()

    def set_user_2(self, value):
        """
        Set user 2 parameter into PDO struct
        :param value: Custom value
        :type value: int
        """
        self.__lock.acquire()
        self.pdo_out.user_2 = value
        self.__lock.release()

    def set_user_3(self, value):
        """
        Set user 3 parameter into PDO struct
        :param value: Custom value
        :type value: int
        """
        self.__lock.acquire()
        self.pdo_out.user_3 = value
        self.__lock.release()

    def set_user_4(self, value):
        """
        Set user 4 parameter into PDO struct
        :param value: Custom value
        :type value: int
        """
        self.__lock.acquire()
        self.pdo_out.user_4 = value
        self.__lock.release()

    def set_Fault_Reset(self):
        """
        Set control word Fault Reset
        """
        self._set_ctrl_word(CMD_FAULT_RESET)

    def set_Shutdown(self):
        """
        Set control word Shutdown
        """
        self._set_ctrl_word(CMD_SHUTDOWN)

    def set_Switch_On(self):
        """
        Set control word Switch On
        """
        self._set_ctrl_word(CMD_SWITCH_ON)

    def set_Enable_Operation(self):
        """
        Set control word Enable Operation
        """
        self._set_ctrl_word(CMD_ENABLE_OP)

    def set_Disable_Operation(self):
        """
        Set control word Disable Operation
        """
        self._set_ctrl_word(CMD_DISABLE_OP)
