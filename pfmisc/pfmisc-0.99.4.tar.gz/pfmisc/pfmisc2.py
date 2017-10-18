#!/usr/bin/env python3.5

import  sys
import  os
import  json

import  pudb

from    _colors         import  Colors
from    debug           import  debug
from    C_snode         import *


class someOtherClass2():
    """
    Some other class
    """

    def __init__(self, *args, **kwargs):
        """
        """

        self.dp             = debug(verbosity=0, level=-1, within = "someOtherClass2")

    def say(self):
        self.dp.qprint("And this is another class!")

class pfmisc2():
    """
    Example of how to use the local misc dependencies
    """

    def col2_print(self, str_left, str_right):
        print(Colors.WHITE +
              ('%*s' % (self.LC, str_left)), end='')
        print(Colors.LIGHT_BLUE +
              ('%*s' % (self.RC, str_right)) + Colors.NO_COLOUR)

    def __init__(self, *args, **kwargs):
        """

        Holder for constructor of class -- allows for explicit setting
        of member 'self' variables.

        :return:
        """
        self.LC             = 40
        self.RC             = 40
        self.args           = None
        self.str_desc       = 'pfmisc'
        self.str_name       = self.str_desc
        self.str_version    = ''

        self.dp             = debug(verbosity=0, level=-1, within='pfmisc2')

    def demo(self, *args, **kwargs):
        """
        Simple run method
        """

        self.dp.qprint("Why hello there, world!")
        other = someOtherClass2()
        other.say()

        for str_comms in ['status', 'error', 'tx', 'rx']: 
            self.dp.qprint("This string is tagged with '%s'" % str_comms, comms = str_comms)

