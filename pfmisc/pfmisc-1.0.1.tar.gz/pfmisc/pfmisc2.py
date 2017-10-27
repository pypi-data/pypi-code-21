#!/usr/bin/env python3.5

import  sys
import  os
import  json
import  pudb

try:
    from    ._colors        import  Colors
    from    .debug          import  debug
    from    .C_snode        import *
except:
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

    def say(self, msg):
        print('\n* Now we are in a different class in this module...')
        print('* Note the different class and method in the debug output.')
        print('* calling: self.dp.qprint(msg):')
        self.dp.qprint(msg)

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

        self.dp             = debug(verbosity   = 0, 
                                    level       = -1, 
                                    within      = 'pfmisc2')

        self.dp2            = debug(verbosity   = 0, 
                                    level       = -1, 
                                    within      = 'pfmisc2',
                                    debugToFile = True, 
                                    debugFile   = '/tmp/pfmisc2.txt')
    def demo(self, *args, **kwargs):
        """
        Simple run method
        """

        print('* calling: self.dp.qprint("Why hello there, world!"):')
        self.dp.qprint("Why hello there, world!")

        print('* calling: self.dp2.qprint("Why hello there, world! In a debugging file!"):')
        self.dp2.qprint("Why hello there, world! In a debugging file!")
        print('* Check on /tmp/pfmisc2.txt')

        other = someOtherClass2()
        other.say("And this is from a different class")

        for str_comms in ['status', 'error', 'tx', 'rx']: 
            print('\n* calling: self.dp.qprint("This string is tagged with %s" % str_comms, ', end='')
            print("comms = '%s')" % str_comms)
            self.dp.qprint("This string is tagged with '%s'" % str_comms, comms = str_comms)

