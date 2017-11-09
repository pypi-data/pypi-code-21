#!/usr/bin/env python
#coding: utf-8

import socket
import fcntl
import struct

class IpUtil:

    @staticmethod
    def get_ip_by_if(ifname):  
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15].encode('utf-8')))[20:24]) 

if __name__ == '__main__':
    try:
        print(IpUtil.get_ip_by_if('em1'))
    except:
        print(IpUtil.get_ip_by_if('eth0'))
