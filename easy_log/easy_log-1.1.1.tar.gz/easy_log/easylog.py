#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import argparse
import textwrap
from collections import OrderedDict
from utils import check_file_path, color_input, bash, Linux, tail, LogPathError

if Linux:
    import readline

def easylog():
    """ main entry, cmdline entry

    :return: None
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('logfile', help='the path for log file')
    parser.add_argument('-n', '--num', type=int, help='filter out only the last n line of log, default 10')
    parser.add_argument('-l', '--level', choices=['debug', 'info', 'warn', 'warning', 'error'], help='filter out only the log line containing this LEVEL')
    parser.add_argument('-t', '--tag', help='filter out only the log line containing this TAG')
    parser.add_argument('-T', '--TAGS', action='store_true', help='print all tags of log')
    parser.add_argument('-f', '--follow', action='store_true', help='print appended log as the log grows')
    parser.add_argument('-i', '--interact', action='store_true', help='enter interact mode')

    args = parser.parse_args()
    try:
        path = check_file_path(args.logfile)
    except LogPathError, e:
        print 'Error: %s' % str(e)
        return

    GeneralCmd(path).start(args)


class Cmd(object):
    def __init__(self, path):
        self._path = path
        self._log = None

    def _print(self):
        """ print current log result """
        for row in self._log:
            print row,

    def _last(self, n):
        """ filter the last n line log """
        if n:
            lines = 0 - abs(int(n))
            self._log = self._log[lines:]

    def _tags(self):
        """ print all tags """
        tags = []
        pattern = re.compile(r' \[(.*)\] ')
        for row in self._log:
            ret = pattern.search(row)
            if ret:
                tag = ret.groups()[0]
                if tag not in tags:
                    tags.append(tag)
                    print tag
        print

    def _filter(self, level=None, tag=None):
        """ filter log by level or tag condition

        :param level: log level include debug, info, warn, warning, error
        :param tag: log tag
        :return: None
        """
        if tag:
            tag = tag.decode('utf-8' if Linux else 'gbk')
        if level == 'warn':
            level = 'warning'

        if level and tag:
            pattern = re.compile(r'\[%s\] \[.*%s.*\] ' % (level.upper(), tag))
        elif level:
            pattern = re.compile(r'\]\[%s\] ' % level.upper())
        elif tag:
            pattern = re.compile(r' \[.*%s.*\] ' % tag)
        else:
            return
        self._log = [row for row in self._log if pattern.search(row)]
        
    def _follow(self, num):
        """ print appended log as the log grows

        :param num: the last num line
        :return:
        """
        if Linux:
            bash('tail -f %s %s' % (self._path, '-n %s' % num if num else ''))
        else:
            tail(self._path, num) if num else tail(self._path)

class GeneralCmd(Cmd):
    @staticmethod
    def _check(args):
        checks = []
        for k, v in args.__dict__.iteritems():
            if k == 'logfile':
                continue
            if v:
                if k in ['TAGS', 'follow', 'interact']:
                    checks.append(True)
                elif k in ['level', 'tag', 'num']:
                    checks.append(False)
        if len(set(checks)) > 1 or checks.count(True) > 1:
            print "%s: %s, %s, %s, %s these options must use alone\n" % \
                  (("\033[1;31mError\033[0m", "\033[32m-i [--interact]\033[0m", "\033[32m-f [--follow]\033[0m",
                    "\033[32m-v [--view]\033[0m", "\033[32m-T [--TAGS]\033[0m")
                   if Linux else ("Error", "'-i [--interact]'", "'-f [--follow]'", "'-v [--view]'", "'-T [--TAGS]'"))
            return False
        else:
            return True

    def start(self, args):
        if self._check(args):
            with open(self._path) as rf:
                self._log = [row.decode('utf-8') for row in rf]

                for arg in sys.argv:
                    if arg.startswith('-f') or arg == '--follow':
                        self._follow(args.num)
                        return
                    elif arg.startswith('-T') or arg == '--TAGS':
                        self._tags()
                        return
                    elif arg.startswith('-i') or arg == '--interact':
                        InteractCmd(self._path).start()
                        return
                    elif arg.startswith('-n') or arg == '--num':
                        self._last(args.num)
                    elif arg.startswith('-t') or arg == '--tag' or arg.startswith('-l') or arg == '--level':
                        self._filter(args.level, args.tag)
                self._print()


class InteractCmd(Cmd):
    pattern_bat = re.compile(r'^ *((([heTvqrp])|(n +\d+)|(f( +\d+)?)|(l +(error|warn|warning|info|debug))|(t +(\S+|".+"|\'.+\'))) +)+$')
    pattern_per = re.compile(r'^n +\d+|f( +\d+)?|l +(error|warn|warning|info|debug)|t +(\S+|".+"|\'.+\')$')

    def __init__(self, path):
        super(InteractCmd, self).__init__(path)
        self._bak = None
        self._orders = OrderedDict()
        self._callback = {
            'p': self._print,
            'n': self._last,
            'l': self._filter,
            't': self._filter,
            'e': self._empty,
            'T': self._tags,
            'r': self._reload,
            'f': self._follow,
            'v': InteractCmd._example,
            'h': InteractCmd._help,
            'q': InteractCmd._quit,
        }

    @staticmethod
    def _quit():
        sys.exit()

    @staticmethod
    def _help():
        """ print help menu """
        if Linux:
            msg = """
                \033[1;32m###   Please select the follow options   ### \033[0m
    
                0) Input \033[32mq\033[0m to quit
                1) Input \033[32mp\033[0m to print filtered log         
                2) Input \033[32mn NUM\033[0m to filter out only the last n line of log
                3) Input \033[32ml {debug,info,warn,warning,error}\033[0m to filter out only the log line containing this LEVEL
                4) Input \033[32mt TAG\033[0m to filter out only the log line containing this TAG
                5) Input \033[32mT\033[0m to print all tags of log
                6) Input \033[32me\033[0m to empty all filter conditions
                7) Input \033[32mr\033[0m to reload log file
                8) Input \033[32mf\033[0m to print appended log as the log grows                
                9) Input \033[32mv\033[0m to print using example
               10) Input \033[32mh\033[0m to print help menu
            """
        else:
            msg = """
                ###   Please select the following options   ### 
                
                0) Input 'q' to quit
                1) Input 'p' to print filtered log         
                2) Input 'n NUM' to filter out only the last n line of log
                3) Input 'l {debug,info,warn,warning,error}' to filter out only the log line containing this LEVEL
                4) Input 't TAG' to filter out only the log line containing this TAG
                5) Input 'T' to print all tags of log
                6) Input 'e' to empty all filter conditions
                7) Input 'r' to reload log file
                8) Input 'f' to print appended log as the log grows                
                9) Input 'v' to print using example
               10) Input 'h' to print help menu                                
            """
        print textwrap.dedent(msg)

    @staticmethod
    def _example():
        """ print help example """
        if Linux:
            msg = """
                 eg.1: 
                     Select Options> \033[32ml error\033[0m
                     Select Options> \033[32mp\033[0m
                 eg.2: 
                     Select Options> \033[32ml error t SendMail p\033[0m
                 eg.3: 
                     Select Options> \033[32ml debug t 'init server' n 5\033[0m
                     Select Options> \033[32mp\033[0m
             """
        else:
            msg = """
                eg.1: 
                    Select Options> l error
                    Select Options> p
                eg.2: 
                    Select Options> l error t SendMail p
                eg.3: 
                    Select Options> l debug t 'init server' n 5
                    Select Options> p                                    
            """
        print textwrap.dedent(msg)

    @staticmethod
    def _check(args):
        checks = []
        for x in args:
            if x in ['T', 'r', 'f', 'v', 'h', 'q']:
                checks.append(True)
            elif x in ['p', 'n', 'l', 't', 'e']:
                checks.append(False)
        if len(set(checks)) > 1 or checks.count(True) > 1:
            print "%s: %s, %s, %s, %s, %s, %s these options must use alone\n" % \
                  (("\033[1;31mError\033[0m", "\033[32mT\033[0m", "\033[32mr\033[0m", "\033[32mf\033[0m",
                    "\033[32mv\033[0m", "\033[32mh\033[0m", "\033[32mq\033[0m")
                   if Linux else ("Error", "'T'", "'r'", "'f'", "'v'", "'h'", "'q'"))
            return False
        else:
            return True

    def _empty(self):
        """ empty all filter conditions """
        self._log = self._bak

    def _reload(self):
        """ reload the log file """
        for k, v in self._orders.iteritems():
            if k == 'n':
                self._callback[k](v)
            elif k == 'l':
                self._callback[k](level=v)
            elif k == 't':
                self._callback[k](tag=v)
            elif k == 'f':
                self._callback[k](v)
            else:
                self._callback[k]()
        self._orders.clear()

    def start(self):
        self._callback['h']()
        while True:
            with open(self._path) as rf:
                self._log = [row.decode('utf-8') for row in rf]
                self._bak = self._log[:]

                while True:
                    try:
                        opts = '%s ' % color_input('Select Options> ')
                    except KeyboardInterrupt:
                        print
                        continue

                    opts_list = opts.split()
                    if not self._check(opts_list):
                        continue

                    if 'r' in opts_list:
                        break

                    for x in opts_list:
                        if len(x) == 1 and x in self._callback.iterkeys():
                            self._orders[x] = None

                    ret = self.pattern_bat.search(opts)
                    if ret:
                        for cmd in ret.groups()[2:]:
                            if cmd and self.pattern_per.search(cmd):
                                cmds = cmd.split()
                                if len(cmds) > 1:
                                    self._orders[cmds[0]] = ' '.join(cmds[1:])
                        self._callback['r']()
                    else:
                        print "%s: Invalid Command. Input %s to print help menu\n" % \
                              (("\033[1;31mError\033[0m", "\033[32mh\033[0m") if Linux else ("Error", "'h'"))


if __name__ == '__main__':
    easylog()
