import os
import sys
import json
import re
import msvcrt
import traceback
import logging
import cProfile
import pstats
import tempfile
import subprocess
from collections import namedtuple
from time import time, sleep, strftime
from contextlib import contextmanager


class Logging(object):
    def __init__(self, level, filename=''):
        Log = namedtuple('Log', 'level func')
        try:
            self.log = {
                'd': Log(logging.DEBUG, logging.debug),
                'i': Log(logging.INFO, logging.info),
                'w': Log(logging.WARNING, logging.warning),
                'e': Log(logging.ERROR, logging.error),
                'c': Log(logging.CRITICAL, logging.critical),
            }[level]
        except KeyError:
            class InvalidLoggingLevel(Exception):
                def __str__(self):
                    return ("The following level characters are allowed: "
                            "'d', 'i', 'w', 'e', 'c'")
            raise InvalidLoggingLevel from None
        args = {'level': self.log.level,
                'format': ' %(asctime)s - ' '%(levelname)s - %(message)s'}
        if filename:
            args['filename'] = filename
        logging.basicConfig(**args)

    def dump(self, msg):
        self.log.func(msg)

    def disable(self):
        logging.disable(self.log.level)


def time_now():
    return strftime('%Y-%m-%d %H:%M:%S')


def day_now():
    return strftime('%Y-%m-%d')


def log_header():
    return ('\n'.join
            (('*' * 79,
              '*' * 30 + time_now() + '*' * 30,
              '*' * 79)))


def myprint(s, p=print, f='log.txt'):
    with open(f, 'a', encoding='utf-8-sig') as fw:
        print(s, file=fw)
    try:
        p(s)
    except UnicodeEncodeError:
        pass


def report_error_to_file(error_file):
    data = ''
    if os.path.isfile(error_file):
        with open(error_file, encoding='utf-8-sig') as fr:
            data = fr.read()
    with open(error_file, 'w', encoding='utf-8-sig') as fw:
        fw.write('{}\n{}\n{}'.format(log_header(),
                                     traceback.format_exc(),
                                     data))


def report_error():
    error_file = 'error.txt'
    report_error_to_file(error_file)
    subprocess.Popen(['notepad', error_file])


def input_with_timeout(prompt, timeout=5):
    print(prompt)
    finishat = time() + timeout
    result = []
    while True:
        if msvcrt.kbhit():
            result.append(msvcrt.getche())
            if result[-1] == b'\r':   # or \n, whatever Win returns;-)
                return b''.join(result)
            sleep(0.1)          # just to yield to other processes/threads
        else:
            if time() > finishat:
                return None


@contextmanager
def mytry(handler, *exceptions):
    try:
        yield
    except exceptions:
        if handler:
            handler()
    except:
        if handler:
            handler()


@contextmanager
def notry(handler, *exceptions):
    yield


@contextmanager
def report_exception(handler=None, *exceptions, final=None, reraise=False):
    try:
        yield
    except exceptions as e:
        if handler:
            handler(e)
        if reraise:
            raise
    except Exception:
        notepad_messagebox(traceback.format_exc())
        if reraise:
            raise
    finally:
        if final:
            final()


@contextmanager
def dir_temp_change(directory):
    cwd = os.getcwd()
    os.chdir(directory)
    yield
    os.chdir(cwd)


def myprofile(command, globals_, locals_, *keys, outfile='profile.txt'):
    cProfile.runctx(command, globals_, locals_, 'profile')
    oldout = sys.stdout
    sys.stdout = open(outfile, 'w')
    p = pstats.Stats('profile')
    p.strip_dirs().sort_stats(*keys).print_stats()
    sys.stdout = oldout
    os.remove('profile')


def settings_from_json(f, myglobals):
    with open(f, encoding='utf-8-sig') as f:
        settings = json.load(f)
        for k, v in settings.items():
            myglobals[re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', k).upper()] = v


def notepad_messagebox(s):
    handle, name = tempfile.mkstemp()
    os.close(handle)
    with open(name, 'w') as f:
        f.write(s)
    subprocess.Popen(['notepad', name])
    # os.remove(name)
