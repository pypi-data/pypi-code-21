#!/usr/bin/env python
# coding: utf-8

import _interface

PortError = _interface.PortError


class Port(object):
    """ Abstraction layer for a more comfortable use """

    def __init__(self, port, addr):
        self.port = port
        self.addr = addr

    def read(self):
        return _interface.read(self.port, self.addr)

    def write(self, value):
        return _interface.write(value, self.port, self.addr)


class PyParport(object):
    """ The main class which implements the interface to the port """

    def __init__(self, base_addres=0x378):
        self.data_address = base_addres
        self.status_address = base_addres + 1
        self.control_address = base_addres + 2

        self.data = Port("d", self.data_address)
        self.status = Port("s", self.status_address)
        self.control = Port("c", self.control_address)
