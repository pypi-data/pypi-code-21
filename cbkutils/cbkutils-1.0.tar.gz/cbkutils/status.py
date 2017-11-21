from __future__ import print_function
from . import spinner
from . import constants as C
from cbkutils.backports.shutil_get_terminal_size import get_terminal_size
import sys

class Status(object):

    def __init__(self, message):
        """ Prints to screen and log file

        Args:
            message (str): The message to print

        """
        self.spinner = spinner.Spinner()

        columns, _lines = get_terminal_size()
        faint = "\033[38;5;243m"
        endc = '\033[0m'
        print("%s %s%s%s " % (message, faint, (">" * (columns - len(message) - 30)), endc) , end='')
        self.spinner.start()


    def end(self, message, style):
        """ Prints to screen and log file

        Args:
            message (str): The message to print
            style (str): A style with which to print

        """
        okicon = '\033[%s;%sm' % (C.FG_BLACK, C.BG_GREEN)
        oktext = '\033[%sm' % (C.FG_GREEN)
        warningicon = '\033[%s;%sm' % (C.FG_BLACK, C.BG_YELLOW)
        warningtext = '\033[%sm' % (C.FG_YELLOW)
        failicon = '\033[%s;%sm' % (C.FG_BLACK, C.BG_RED)
        failtext = '\033[%sm' % (C.FG_RED)
        pendingicon = "\033[38;5;0;48;5;243m"
        pendingtext = '\033[%sm' % (C.FAINT)
        columns, _lines = get_terminal_size()
        endc = '\033[0m'
        self.spinner.stop()
        if style == 'ok':
            print(u"%s %s %s %s%s%s" % (okicon, u'\u2714', endc, oktext, message, endc))
        elif style == 'warning':
            print(u"%s %s %s %s%s%s" % (warningicon, u'!', endc, warningtext, message, endc))
        elif style == 'fail':
            print(u"%s %s %s %s%s%s" % (failicon, u'\u2715', endc, failtext, message, endc))
        elif style == 'pending':
            print(u"%s %s %s %s%s%s" % (pendingicon, u"\u29D7", endc, pendingtext, message, endc))
