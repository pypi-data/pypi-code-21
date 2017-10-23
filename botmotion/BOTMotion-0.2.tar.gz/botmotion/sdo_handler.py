# BOT Motion Module
#
# SDO Handler
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

from sdo_error_code import *
from ethernet_socket import *
from config import *
from debug_printing import *

SDO_REQUEST = 0x2
SDO_RESPONSE = 0x3

SDO_DL_REQUEST = 0x1
SDO_UL_REQUEST = 0x2

SDO_TRANSFER_TYPE_EX = 0x1
SDO_TRANSFER_TYPE_NO = 0x0

SDO_COMPLETE_ACCESS_ENTRY = 0x0
SDO_COMPLETE_ACCESS_OBJ   = 0x1

SDO_DATA_SET_SIZE = 0x0 # 4 Octet data

class ExceptionSDO(Exception):
    """
    Class for SDO related exceptions
    """
    pass


class SDO_Struct():
    """
    SDO message struct
    """
    def __init__(self):
        self.coe_header = 0         # COE Header Service (Request or Download
        self.transfer_type = 0
        self.complete_access = 0    # 0: entry addressed with index and subindex will be uploaded
                                    # 1: complete object will be uploaded, subindex shall be zero
                                    # (subindex 0 included) or one (subindex 0 excluded)
        self.cmd_specifer = 0       # Upload request or download request
        self.index = 0
        self.subindex = 0
        self.value = 0

class SDO_Handler(ExThread):
    """
    SDO handler. Downloaded and uploaded SDO dictionary entries.
    """
    def __init__(self, id, address, port, sdo_config):
        """
        Initialized SDO handler
        :param id: object id
        :type id: uint
        :param address: IP address
        :type address: string
        :param port: tcp port
        :type port: uint
        """
        super(SDO_Handler, self).__init__()
        self.__id = id
        self.__object_dict = sdo_config
        self.__coe_header = SDO_REQUEST << 12 | 0x0
        self.__sdo_header_dl = SDO_DL_REQUEST << 5 & 0x70 | SDO_COMPLETE_ACCESS_ENTRY << 4 & 0x10 | SDO_DATA_SET_SIZE << 2 & 0xC | SDO_TRANSFER_TYPE_EX << 1 & 0x2 | 0x1
        self.__sdo_header_ul = SDO_UL_REQUEST << 5 & 0x70 | SDO_COMPLETE_ACCESS_ENTRY << 4 & 0x10
        self.__printer = DebugPrint(self.__id, 'SDO Handler')

        self.__ethernet_socket = EthernetSocket(self.__id, IF_NAME, address, port, 'TCP')
        self.__ethernet_socket.connect()

    def close(self):
        """
        Close socket
        """
        self.__ethernet_socket.close()

    def __get_sdo_index(self, sdo):
        """
        Return index of SDO entry.
        :param sdo: SDO entry
        :type sdo: list
        :return: SDO index
        :rtype: uint
        """
        return sdo[0]

    def __get_sdo_subindex(self, sdo):
        """
        Return subindex of SDO entry.
        :param sdo: SDO entry
        :type sdo: list
        :return: SDO subindex
        :rtype: uint
        """
        return sdo[1]

    def __get_sdo_value(self, sdo):
        """
        Return value of SDO entry.
        :param sdo: SDO entry
        :type sdo: list
        :return: SDO value
        :rtype: int
        """
        return sdo[2]

    def _make_sdo_dl_paket(self, sdo):
        """
        Encode SDO download message.
        :param sdo: SDO entry.
        :type sdo: list
        :return: encode SDO entry
        :rtype: binary string
        """
        struct_string = '<HBHBi'
        if (type(self.__get_sdo_value(sdo)) is float):
            struct_string = '<HBHBf'

        return struct.pack(struct_string,
                               self.__coe_header,
                               self.__sdo_header_dl,
                               self.__get_sdo_index(sdo),
                               self.__get_sdo_subindex(sdo),
                               self.__get_sdo_value(sdo))

    def _make_sdo_ul_paket(self, sdo):
        """
        Encode SDO upload message.
        :param sdo: SDO entry.
        :type sdo: list
        :return: encode SDO entry
        :rtype: binary string
        """
        return struct.pack('<HBHBI', self.__coe_header,
                           self.__sdo_header_ul,
                           self.__get_sdo_index(sdo),
                           self.__get_sdo_subindex(sdo),
                           0)

    def _decode_sdo_response(self, data):
        """
        Decode SDO response
        :param data: Received SDO data
        :type data: binary string
        :return: SDO entry as struct
        :rtype: sdo_struct
        """
        if data:
            sdo = SDO_Struct()
            sdo.coe_header = struct.unpack_from('B', data, 1)[0] >> 4 & 0xf
            sdo.transfer_type = struct.unpack_from('B', data, 2)[0] >> 1 & 0x1
            sdo.complete_access = struct.unpack_from('B', data, 2)[0] >> 4 & 0x1
            sdo.cmd_specifier = struct.unpack_from('B', data, 2)[0] >> 5 & 0x7
            sdo.index = struct.unpack_from('H', data, 3)[0]
            sdo.subindex = struct.unpack_from('B', data, 5)[0]
            sdo.value = struct.unpack_from('I', data, 6)[0]
            return sdo
        else:
            return None

    def _check_sdo_response(self, sdoin, sdoout):
        """
        Check if SDO response is valid
        :param sdoin: Received SDO data
        :type sdoin: sdo_struct
        :param sdoout: SDO dict entry
        :type sdoout: list
        """
        val = sdoin.coe_header == SDO_RESPONSE and \
           sdoin.index == self.__get_sdo_index(sdoout) and \
           sdoin.subindex == self.__get_sdo_subindex(sdoout)

        if not val:
            self.__printer.printf('\n\n\tWARNING: SDO Error\n')
            self.__printer.printf('\tService: 0x%x\n' % int(sdoin.coe_header))
            self.__printer.printf('\tIndex: 0x%x\n' % int(sdoin.index) )
            self.__printer.printf('\tSubindex: %d\n' % sdoin.subindex )
            self.__printer.printf('\tError Code: %s\n\n' % sdo_error_dict[sdoin.value] )
            raise ExceptionSDO('EXCEPTION:\nSDO Error: %s' % sdo_error_dict[sdoin.value])

    def set_sdo_entry(self, index, subindex, value):
        """
        Set custom SDO entry into dictionary
        :param index: SDO Index
        :type index: uint
        :param subindex:  SDO Subindex
        :type subindex: uint
        :param value: SDO value
        :type value: int
        """
        for entry in self.__object_dict:
            if entry[0] == index and entry[1] == subindex:
                entry[2] = value

    def download_all(self):
        """
        Download the whole SDO dictionary. Starts thread and wait until thread finished
        """
        self.start()
        self.join()

    def upload_single_sdo(self, index, subindex):
        sdo_paket = self._make_sdo_ul_paket([index, subindex])
        recv_success = False
        try_counter = 0

        sdo_resp = None

        while not recv_success:
            self.__ethernet_socket.send(sdo_paket)
            recv = self.__ethernet_socket.recv()
            if recv:
                recv_success = True
                sdo_resp =  self._decode_sdo_response(recv[0])
            else:
                try_counter += 1

            if try_counter == 5:
                raise ExceptionSDO('Not able to upload SDOs from %s' % self.__ethernet_socket.get_slave_ip())

        return sdo_resp


    def run_with_exception(self):
        """
        SDO thread. Sends the whole SDO dictionary.
        """
        self.__printer.printf('Update SDOs...')

        for sdo in self.__object_dict:
            recv_success = False
            try_counter = 0
            sdo_paket = self._make_sdo_dl_paket(sdo)

            while not recv_success:
                self.__ethernet_socket.send(sdo_paket)
                recv = self.__ethernet_socket.recv()
                if recv:
                    recv_success = True
                    sdo_resp = self._decode_sdo_response(recv[0])
                    self._check_sdo_response(sdo_resp, sdo)
                else:
                    try_counter += 1

                if try_counter == 5:
                    raise ExceptionSDO('Not able to download all SDOs to %s' % self.__ethernet_socket.get_slave_ip())

        #self.close()
        self.__printer.printf('done\n')
