# -*- coding: utf-8 -*-

class Equipment(object):

    def __init__(self, name, ip, port):
        self.name = name
        self.ip = ip
        self.port = port

    def __str__(self):
        return '{}({}:{})'.format(self.name, self.ip, self.port)
