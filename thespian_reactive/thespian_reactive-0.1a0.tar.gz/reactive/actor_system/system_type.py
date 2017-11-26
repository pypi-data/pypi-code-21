'''
A system types enum for better understanding Thespian.  This is used
when establishing an ActorSystem.

Created on Oct 31, 2017

@author: aevans
'''

def simple_base():
    return None

def multiproc_queue_base():
    return "multiprocQueueBase"

def multiproc_tcp_base():
    return "multiprocTCPBase"
