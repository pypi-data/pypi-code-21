import platform
import sys,os

from termcolor import colored
from contextlib import contextmanager

import logging

if os.getenv("DEBUG"):
    file = os.getenv('file')
    print(colored("log -> ",'red'), file,'debug start')
    logging.basicConfig(
        level=logging.DEBUG,
        filename=file,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    )
else:
    file = os.getenv('file')
    logging.basicConfig(
        level=logging.INFO,
        filename=file,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    )

PY = platform.python_version()[:2]


def show(*contents, **kargs):
    """
    @log: set True  to use logging module.
    @c: set color [red/yellow/blue/cyan/magenta]
    @a: set attrs '["underline"/"blink"/"bold"]'
    @on: set background [on_red/on_blue]
    """
    if 'log' in kargs and kargs['log'] == True:
        f = getattr(logging, kargs['k'])
        if 'c' in kargs:
            color = kargs['c']
        else:
            color = None

        if 'on' in kargs:
            on = kargs['on']
        else:
            on = None

        if 'a' in kargs:
            a = kargs['a']
        else:
            a = []

        s = colored("[+] ",'blue') + colored(' '.join([str(i) for i in contents]), color, on, attrs=a)
        f(s)

    else:    
        L("[+]",end=' ', color='blue')
        L(*contents, **kargs)


def L(*contents, **kargs):
    """
    @c: set color [red/yellow/blue/cyan/magenta]
    @a: set attrs '["underline"/"blink"/"bold"]'
    @on: set background [on_red/on_blue]
    """
    on = ''
    c = ''
    end = '\n'
    column = ''
    row = ''
    if 'on' in kargs:
        on = kargs['on']
    if 'color' in kargs:
        c = kargs['color']
    if 'end' in kargs:
        end = kargs['end']
    
    if 'c' in kargs:
        column = kargs['c']

    if 'r' in kargs:
        row = kargs['r']

    res = ' '.join([str(i) for i in contents])
    if c:
        if on:
            res = colored(res, c, on)
        else:
            res = colored(res, c)

    if row and column:
        with LogControl.jump(row,column):
            sys.stdout.write(res + end)
            sys.stdout.flush()
            return len(res+end)

    sys.stdout.write(res + end)
    sys.stdout.flush()
    return len(res+end)

class LogControl:
    INFO = 0x08
    ERR = 0x00
    OK = 0x04
    WRN = 0x02
    FAIL = 0x01
    LOG_LEVEL = 0x04

    SIZE = tuple([ int(i) for i in os.popen("tput lines && tput cols ").read().split()])

    @staticmethod
    def got_size():
        SIZE = tuple([ int(i) for i in os.popen("tput lines && tput cols ").read().split()])
        return SIZE

    @staticmethod
    def save(p='civis'):
        """
        civis set will let p hidden.
        cnorm set will let p display.
        """
        os.system("tput sc  && tput civis && tput " + p)

    @staticmethod
    def load():
        """
        civis set will let p hidden.
        cnorm set will let p display.
        """
        os.system("tput rc  && tput cnorm ")


    @staticmethod
    @contextmanager
    def jump(line, col):
        """
        @cur can set cursor display or hidden
        @line, @col: cursor to jump.
        """
        try:
            # if not cur:
            #     os.system("tput civis")
            os.system(" tput cup %d %d  " % (line, col))
            
            yield
        finally:
            # os.system("tput rc")
            pass



    @staticmethod
    def cl(line):
        os.system("tput sc  && tput cnorm  && tput cup %d 0 && tput el  && tput rc && tput cnorm")

    @staticmethod
    def loc(line, col, el=False):
        os.system("tput cup %d %d " % (line, col))
        if el:
            os.system("tput el")

