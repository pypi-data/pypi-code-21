'''
The actor state enumeration.  This is for maintenance and other tasks as actor
state in Thespian is generally not accessible.  It is left for the user and
program to maintain higher level streams.  States are CREATED, LIMBO, RUNNING,
and TERMINATED.

Created on Oct 29, 2017

@author: aevans
'''

from enum import Enum


class ActorState(Enum):
    CREATED = 1
    LIMBO = 2
    TERMINATED = 3
    RUNNING = 4