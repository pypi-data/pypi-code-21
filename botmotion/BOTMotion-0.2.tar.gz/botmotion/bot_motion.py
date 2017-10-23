# BOT Motion Module
#
# BOT Motion Module
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

from sdo_handler import *
from pdo_handler import *
from init_drive import *
from debug_printing import *
from sdo_read_config import *

PDO_INIT_TIMEOUT = 3  # sec

class ExceptionInitPDO(Exception):
    pass

class ExceptionInitNode(Exception):
    pass

class ExceptionWrongOpMode(Exception):
    pass

class ExceptionTimeout(Exception):
    pass

class Timeout(object):

    def __init__(self, timeout, context_name):
        self.__timeout = timeout
        self.__start_time = time.clock()
        self.__context_name = context_name

    def check(self, info):
        if (time.clock() - self.__start_time) >= self.__timeout:
            raise ExceptionTimeout('Timeout %s -> %s' % (self.__context_name, info))


class BotMotion(object):
    """
    Bot Motion main class. Calls PDO and SDO handler.
    """

    number_inst = 0
    """ number_inst is number of objects. Equals number of BOT Motion axis """
    address_port_list = []
    """ address_port_list is list of all found nodes """

    def __init__(self, address, op_mode):
        """
        Initializer for BotMotion module
        :param address: IP-address for axis
        :type address: string
        """
        BotMotion.number_inst += 1
        self.__id = BotMotion.number_inst
        self.__sdo_port = TCP_PORT + self.__id * 2
        self.__pdo_port = UDP_PORT + self.__id * 2
        self.__address = address
        self.__op_mode = op_mode
        self.__printer = DebugPrint(self.__id, 'Motor')
        self.__printer.printf('Address: %s, Port pdo: %d, sdo %d\n' % (address, self.__pdo_port,
                                                                       self.__sdo_port))
        self.__pdo_handler = None
        self.__sdo_handler = None
        self.__init_sdo()
        # absolutely not nice, but necessary, since we have to wait until timeout of socket occurred.
        # After timeout TCP connection will be closed with 'FIN ACK'
        time.sleep(0.1)
        self.__init_pdo()

    def __find_nodes(self):
        """
        In case of DHCP this method is searching for nodes and saves all addresses in
        a class-attribute list.
        :exception: ExceptionInitNode
        """

        if BotMotion.number_inst == 1:
            init_node = Init_Drive()
            BotMotion.address_port_list = init_node.search_nodes()
            init_node.close()

            if not BotMotion.address_port_list:
                raise ExceptionInitNode('No nodes found')

    def __assign_ports(self):
        """
        Assigns for every found node two ports (TCP and UDP)
        :exception: ExceptionInitNode
        """
        index = [(i, l.index(self.__address))
                 for i, l in enumerate(BotMotion.address_port_list)
                 if self.__address in l]
        if len(index) == 1:
            index = index[0][0]
            print BotMotion.address_port_list[index][1], BotMotion.address_port_list[index][2]
            self.__sdo_port = BotMotion.address_port_list[index][1]
            self.__pdo_port = BotMotion.address_port_list[index][2]
        elif len(index) > 1:
            raise ExceptionInitNode('Too many nodes with IP %s found' % (self.__address))
        else:
            raise ExceptionInitNode('No node with IP %s found' % (self.__address))

    def __init_sdo(self):
        """
        Initialization of SDOs. Downloads whole dictionary to the node.
        """
        sdo_parser = SDO_Read_Config(SDO_CONFIG_FILE)
        sdo_config = sdo_parser.parse_file()[sdo_ip_id[self.__address]]
        self.__sdo_handler = SDO_Handler(self.__id, self.__address, self.__sdo_port, sdo_config)
        self.__sdo_handler.download_all()
        exc = self.__sdo_handler.check_for_exception()
        #self.__sdo_handler.close()
        if exc:
            print exc
            sys.exit(1)


    def __set_op_mode(self):
        if self.__op_mode == OPMODE_CSV:
            self.__pdo_handler.set_opmode_csv()
        elif self.__op_mode == OPMODE_CSP:
            self.__pdo_handler.set_opmode_csp()
        elif self.__op_mode == OPMODE_CST:
            self.__pdo_handler.set_opmode_cst()
        else:
            raise ExceptionWrongOpMode('Not supported operation mode: ' + self.__op_mode)


    def __init_pdo(self):
        """
        Initialization of PDOs. Sets CiA402 states and operation.
        """

        try:
            self.__pdo_handler = PDO_Handler(self.__id, self.__address, self.__pdo_port)

            self.__set_op_mode()

            # Reset Fault (just in case)
            self.__printer.printf('Reset fault\n')
            self.__pdo_handler.set_Fault_Reset()

            to = Timeout(PDO_INIT_TIMEOUT, 'Reset fault')
            # Wait for status change
            while self.__pdo_handler.get_statusword() != 'Switch on disabled':
                self.__pdo_handler.check_for_exception()
                to.check(self.__pdo_handler.get_statusword())

            # Shutdown
            self.__printer.printf('Shutdown\n')
            self.__pdo_handler.set_Shutdown()

            to = Timeout(PDO_INIT_TIMEOUT, 'Shutdown')
            while self.__pdo_handler.get_statusword() != 'Ready to switch on':
                self.__pdo_handler.check_for_exception()
                to.check(self.__pdo_handler.get_statusword())

            # Switch on
            self.__printer.printf('Switch on\n')
            self.__pdo_handler.set_Switch_On()

            to = Timeout(PDO_INIT_TIMEOUT, 'Switch on')
            # Note: Automatic transition to Enable Operation state after executing SWITCHED ON state
            # functionality.
            while self.__pdo_handler.get_statusword() != 'Switched on' \
                    and self.__pdo_handler.get_statusword() != 'Operation enabled':
                self.__pdo_handler.check_for_exception()
                to.check(self.__pdo_handler.get_statusword())

            #self.__pdo_handler.set_update_slave_pid()

            # Set operation enabled
            self.__printer.printf('Operation enabled\n')
            self.__pdo_handler.set_Enable_Operation()

            to = Timeout(PDO_INIT_TIMEOUT, 'Operation enabled')
            while self.__pdo_handler.get_statusword() != 'Operation enabled':
                self.__pdo_handler.check_for_exception()
                to.check(self.__pdo_handler.get_statusword())

        except Exception as e:
            self.__pdo_handler.close()
            raise e

    def set_velocity(self, velocity):
        """
        Set velocity. Value will be stored in PDO struct.
        Via join_with_exception we check, if in PDO thread an exception is occurred.
        :param velocity: Velocity for axis
        :type velocity: signed int
        """
        self.__pdo_handler.set_velocity(velocity)
        self.__pdo_handler.check_for_exception()


    def set_position(self, position):
        """
        Set position. Value will be stored in PDO struct.
        Via join_with_exception we check, if in PDO thread an exception is occurred.
        :param position: Position for axis
        :type position: signed int
        """
        self.__pdo_handler.set_position(position)
        self.__pdo_handler.check_for_exception()

    def set_sdo_entry(self, index, subindex, value):
        """
        Set manually an SDO entry.
        :param index: Index for SDO entry
        :type index: unsigned int
        :param subindex: Subindex for SDO entry
        :type subindex: unsigned int
        :param value: Value for SDO entry
        :type value: int
        """
        if self.__sdo_handler:
            self.__sdo_handler.set_sdo_entry(index, subindex, value)

    def upload_sdo_entry(self, index, subindex):
        return self.__sdo_handler.upload_single_sdo(index, subindex)

    def get_pdo_in(self):
        """
        Returns the incoming PDO struct (for printing purpose or similar)
        :return: incoming PDO struct
        :rtype: pdo_in_struct
        """
        if self.__pdo_handler:
            return self.__pdo_handler.pdo_in
        else:
            return None

    def get_pdo_out(self):
        """
        Returns the outgoing PDO struct
        :return: incoming PDO struct
        :rtype: pdo_out_struct
        """
        if self.__pdo_handler:
            return self.__pdo_handler.pdo_out
        else:
            return None

    def close(self):
        """
        Close pdo and sdo handler
        """
        if self.__pdo_handler:
            self.__pdo_handler.close()

        if self.__sdo_handler:
            self.__sdo_handler.close()
