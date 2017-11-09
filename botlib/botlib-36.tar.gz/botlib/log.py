# BOTLIB Framework to program bots
#
# botlib/log.py
#
# Copyright 2017 B.H.J Thate
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice don't have to be included.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" log module to set standard format of logging. """

from .static import BOLD, RED, YELLOW, GREEN, BLUE, ENDC, LEVELS

import logging.handlers
import logging
import socket
import os

homedir = os.path.expanduser("~")
curdir = os.getcwd()

try:
    hostname = socket.getfqdn()
except:
    hostname = "localhost"

logdir = homedir + os.sep + ".botlog" + os.sep
logcurdir = curdir + os.sep + "logs" + os.sep

datefmt = '%H:%M:%S'
format_large = "%(asctime)-8s %(module)10s.%(lineno)-4s %(message)-50s (%(threadName)s)"
format_source = "%(asctime)-8s %(message)-55s (%(module)s.%(lineno)s)"
format_time = "%(asctime)-8s %(message)s"
format_log = "%(message)s"

class DumpHandler(logging.StreamHandler):

    """ Logger that logs nothing. """

    def emit(self, record):
        pass

class Formatter(logging.Formatter):

    """ Formatter that strips coloring (even more yes!) from the Logger. """

    def format(self, record):
        target = str(record.msg)
        if not target:
            target = " "
        if target[0] in [">", "<", "!", "#", "^", "-", "&"]:
            target = target[2:]
        record.msg = target
        return logging.Formatter.format(self, record)

def cdir(path):
    """ create directory. """
    res = ""
    for p in path.split(os.sep):
        res += "%s%s" % (p, os.sep)
        padje = os.path.abspath(os.path.normpath(res))
        try:
            os.mkdir(padje)
        except (IsADirectoryError, NotADirectoryError, FileExistsError):
            pass
    return True

def log_cb(event):
    event.save()
    
log_cb.cbs = ["PRIVMSG", "JOIN", "PART", "QUIT", "CLI"]

def log(level, error):
    """ log a line on given level. """
    l = LEVELS.get(str(level).lower())
    logging.log(l, error)

def loglevel(level, logpath=""):
    """ set loglevel to provided level. logpath can be used to define the directory to log into. """
    from .space import cfg
    from .utils import cdir
    if not os.path.isdir(cfg.logdir or logdir):
        cdir(logdir)
    if not os.path.isdir(logcurdir):
        cdir(cfg.logdir or logcurdir)
    level = level.upper()
    logger = logging.getLogger("")
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    dhandler = DumpHandler()
    logger.setLevel(level)
    logger.addHandler(dhandler)
    if cfg.test:
        fmt = format_source
    else:
        fmt = format_log
    if cfg.verbose:
        formatter = Formatter(fmt, datefmt=datefmt)
        ch = logging.StreamHandler()
        ch.propagate = False
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    else:
        formatter_clean = Formatter(format_log, datefmt=datefmt)
        filehandler = logging.handlers.TimedRotatingFileHandler(os.path.join(logpath or cfg.logdir, "bot.log"), 'midnight')
        filehandler.setLevel(level)
        filehandler.setFormatter(formatter_clean)
        logger.addHandler(filehandler)
    return logger
