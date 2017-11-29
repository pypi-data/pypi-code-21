#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
from contextlib import contextmanager
__author__ = 'Kandit'
import logging
import sys
from collections import namedtuple
import atexit
DEFAULT_FORMAT='%(asctime)s %(levelname)s %(message)s'



def Region(latmin,latmax,lonmin,lonmax):
    Reg = namedtuple("Region", ["latrange","lonrange"])
    Latrange = namedtuple("Latrange", ["min","max"])
    Lonrange = namedtuple("Lonrange", ["min","max"])
    Reg.contains= lambda self,lat,lon: True if latmin<=lat <=latmax and lonmin <= lon <= lonmax else False
    return Reg(Latrange(latmin,latmax), Lonrange(lonmin, lonmax))




class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def getPrint(color):
        def myprint(st):
            print color + st + bcolors.ENDC
        return myprint








class DFH(object):
    def __init__(self, done_file_name, key=lambda x:x, maxlen=4000):
        self.key=key
        touch(done_file_name)
        self.done_file_name = done_file_name
        (self.__donefile, self.__donelist) = self.__read_done__()
        self.maxlen = maxlen
        self.crop_done()





    def crop_done(self):
        maxlen = self.maxlen
        with open(self.done_file_name, "rw+") as donefl:
            donelist_raw = sorted(donefl.readlines(), key=self.key)
            l = len(donelist_raw)
            if l > maxlen:
                newlist = donelist_raw[(l - maxlen):]
                donefl.seek(0)
                donefl.writelines(newlist)
                donefl.close()

    def __read_done__(self):
        newlist = set(map(lambda s: s.strip(), open(self.done_file_name).readlines()))
        return open(self.done_file_name, "a"), newlist


    def sort_log(self, reverse=False):

        donelist_raw = open(self.done_file_name, "r").readlines()
        donelist_raw = sorted(donelist_raw,key=self.key)
        newdonefl = open(self.done_file_name, "w")
        newdonefl.writelines(donelist_raw)
        newdonefl.close()

    def mark_done(self, item):
        self.__donefile.write(item + "\n")
        self.__donefile.flush()


    def is_done(self, url):
        return url in self.__donelist


    def filter_done(self, itemlst):
        return [u for u in itemlst if not self.is_done(u)]


@contextmanager
def working_directory(path):
    prev_cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def init_logger(logfile = os.path.splitext(os.path.normpath(sys.argv[0]))[0] +".log" ,
                FORMAT=DEFAULT_FORMAT):

    logfile = touch(logfile)
    logger = logging.getLogger(os.path.splitext(os.path.basename(os.path.normpath(sys.argv[0])))[0])
    print os.path.splitext(os.path.basename(os.path.normpath(sys.argv[0])))[0]
    logger.errFlag = False

    def myerrorfun(x):
        logger.errFlag = True
        logger.native_error(x)

    logger.native_error = logger.error
    logger.error = myerrorfun
    file_handler = logging.FileHandler(logfile)
    stream_handler = logging.StreamHandler()  # stt err
    formatter = logging.Formatter(FORMAT)
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.DEBUG)
    return logger


def du(path):
    """disk usage in human readable format (e.g. '2,1GB')"""
    try:
        bytess = subprocess.check_output(['du', '-s', path]).split()[0].decode('utf-8')
    except:
        bytess = "NaN"
    return bytess


def touch(fname, times=None):
    if not os.path.exists(fname):
        with open(fname, 'a'):
            os.utime(fname, times)
    return fname


class Multierror(Exception):
    errors = []

    def __init__(self, *args, **kwargs):
        super(Multierror, self).__init__(*args, **kwargs)


    def addError(self, ex):
        self.errors.append(ex)

    def addErrors(self, exs):
        self.errors.extend(exs)



def run_async(threadname):
    def run_in_thread(func):
        """
            run_async(func)
                function decorator, intended to make "func" run in a separate
                thread (asynchronously).
                Returns the created Thread object

                E.g.:
                @run_async
                def task1():
                    do_something

                @run_async
                def task2():
                    do_something_too

                t1 = task1()
                t2 = task2()
                ...
                t1.join()
                t2.join()
        """
        from threading import Thread
        from functools import wraps

        @wraps(func)
        def async_func(*args, **kwargs):
            func_hl = Thread(target = func, args = args, kwargs = kwargs,name = threadname)
            func_hl.start()
            return func_hl

    return run_in_thread


def mkdirp(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)