#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum

class VNFState(Enum):
    
    STARTING = 1
    RUNNING = 2
    STOP_REQUESTED = 3
    RESTART_REQUESTED = 4
    RESTARTING = 5
    SHUTDOWN = 6
    SVC_RESTART_REQUESTED = 7
    UNDEFINED = 999
