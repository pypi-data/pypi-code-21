import struct
import time
import sys

from ethernet_socket import *
from config import *
from pdo_printing import *

SEARCH_TIME = 4 # in seconds


class Init_Drive(EthernetSocket):

    def __init__(self):
        super(Init_Drive, self).__init__(IF_NAME, '', UDP_PORT, 'UDP')
        self.__found_nodes = []
        self.set_broadcast()
        self.address_port_list = [] # IP, TCP, UDP
        self.__port = TCP_PORT + 2

    def _assign_port_numbers(self):
        if len(self.__found_nodes) > 0:
            for addr in self.__found_nodes:
                self.address_port_list.append([addr, self.__port, self.__port+1])
                self.__port += 2

    def search_nodes(self):
        packet = struct.pack('<H', 0xc1a4)
        print 'Searching nodes...'
        time0 = time.time()
        time_send = time0

        while(1):

            msg = self.recv()
            if msg:
                #print 'data', msg[0], 'address', msg[1]
                #print msg
                if msg[1][0] != self.host and len(msg[0]) == 1:
                    data = struct.unpack('B', msg[0])[0]
                    if data == 0xff and not msg[1][0] in self.__found_nodes:
                        self.__found_nodes.append(msg[1][0])

            time1 = time.time()
            time2 = time1 - time_send
            # Send every 300 ms a broadcast message
            if round(time2, 1) > 0.3:
                time_send = time1
                self.sendto(packet, ('<broadcast>', UDP_PORT) )

            time_passed = time1 - time0

            progress_bar(time_passed, SEARCH_TIME)

            if time_passed > SEARCH_TIME:
                break

        sys.stdout.write('\ndone\n')
        sys.stdout.flush()

        self._assign_port_numbers()
        if  len(self.address_port_list) > 0:
            print self.address_port_list

        return self.address_port_list
