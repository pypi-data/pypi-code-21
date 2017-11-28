'''
Created on Nov 14, 2017

@author: Salim
'''


class FormatTypeNotAcceptable(Exception):
    '''
        Exception to FormatTypeNotAcceptable
    '''
    def __init__(self, msg):
        Exception.__init__(self, msg)
    
    
    
class InvalidStateException(Exception):
    '''
        Exception to InvalidStateException
    '''
    def __init__(self, msg):
        Exception.__init__(self, msg)