#!/usr/bin/env python
#coding: utf-8
import time  
import struct  
import logging
import threading
from multiprocessing import Process
from socket import *  


class MulticastUtil:

    def __init__(self, sip, sport, mgrp, mport, mttl):
        self.__sip = sip
        self.__sport = sport
        self.__mgrp = mgrp
        self.__mport = mport
        self.__mttl = mttl
        self.__logger = logging.getLogger('sts_master')
        self.__logger.debug("sip: %s, sport: %d, mgrp: %s, mport: %d, mttl: %d" %
                (sip, sport, mgrp, mport, mttl))
	
    def send(self, data):
        sock = socket(AF_INET, SOCK_DGRAM,IPPROTO_UDP)  
        sock.bind((self.__sip, self.__sport)) 
        ttl_bin = struct.pack('@i', self.__mttl)  
        sock.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, ttl_bin)  
        status = sock.setsockopt(IPPROTO_IP,  
                            IP_ADD_MEMBERSHIP,  
                            inet_aton(self.__mgrp) + inet_aton(self.__sip))

        data += '\0'
        return sock.sendto(data.encode('utf-8'), (self.__mgrp, self.__mport))

    def serve(self, func):
        sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)  
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  
        sock.bind(('0.0.0.0', self.__mport))  
        status = sock.setsockopt(IPPROTO_IP,  
                                IP_ADD_MEMBERSHIP,  
                                inet_aton(self.__mgrp) + inet_aton('0.0.0.0'));  
  
        #sock.setblocking(1)  
        while True:  
            print("wait for recv ...")
            try:  
                data, addr = sock.recvfrom(1024)  
                func(data, addr)
            except Exception as e:  
                self.__logger.exception(e)
            else:  
                self.__logger.debug("Receive data!")  
                self.__logger.debug("TIME: %s" % time.time())
                self.__logger.debug("FROM: %s-%s" % (addr[0], addr[1]))  
                self.__logger.debug("DATA: %s" % data)
            time.sleep(1)
        else:
            sock.close()
                

    def serve_noblock(self, func):
        #process = Process(target=self.serve, args=(func,))
        #process.start()
        thread = threading.Thread(target=self.serve, args=(func,))
        thread.start()
      
if __name__ == "__main__":  
    m = MulticastUtil('10.0.2.15', 1234, '224.1.1.1', 9999, 255)

    def dis(data):
        print("=========")
        print(data)
        print("=========")

    m.recv(dis)
