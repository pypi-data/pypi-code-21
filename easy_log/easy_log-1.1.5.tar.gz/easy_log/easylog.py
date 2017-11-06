#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import argparse
import textwrap
from collections import OrderedDict
from utils import init_config, get_log_path, check_file_path, list_remove_duplicate, color_input, bash, Linux, tail, LogPathError, LogParaError

try:
    import readline
except ImportError:
    pass


def easylog():
    """ main entry, cmdline entry

    :return: None
    """
    init_config()

    parser = argparse.ArgumentParser()
    parser.add_argument('logfile', nargs='?', help='the path for log file')
    parser.add_argument('-n', '--num', type=int, help='filter out only the last n line of log, default 10')
    parser.add_argument('-l', '--level', choices=['debug', 'info', 'warn', 'warning', 'error'], help='filter out only the log line containing this LEVEL')
    parser.add_argument('-t', '--tag', action='store_true', help='print all tags of log')
    parser.add_argument('-w', '--words', help='filter out only the log line containing these words')
    parser.add_argument('-c', '--clear', action='store_true', help='empty the log file')
    parser.add_argument('-f', '--follow', action='store_true', help='print appended log as the log grows')
    parser.add_argument('-i', '--interact', action='store_true', help='enter interact mode')

    args = parser.parse_args()
    try:
        if args.logfile:
            path = get_log_path(check_file_path(args.logfile))
        else:
            path = get_log_path('')
    except LogParaError, e:
        print 'Error: %s' % str(e)
        return
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

    def _clear(self):
        """ empty the log file """
        try:
            choice = raw_input('Do you want to empty log file ?(n/y) ')
        except KeyboardInterrupt:
            print 'Cancel to empty the log file !'
            return

        choice = choice.strip().lower()
        if choice == 'y' or choice == 'yes':
            with open(self._path, 'w') as wf:
                wf.truncate()

            if self._log:
                self._log = []
            print 'Empty the log file successfully !'
        else:
            print 'Cancel to empty the log file !'

    def _tag(self):
        """ print all tags """
        tags = []
        pattern = re.compile(r'\[(.*?)\]')
        for row in self._log:
            for tag in pattern.findall(row):
                tag = '%s\n' % tag
                if tag not in tags:
                    tags.append(tag)
        self._log = tags

    def _filter(self, level=None, words=None):
        """ filter log by level or tag condition

        :param level: log level include debug, info, warn, warning, error
        :param words: the word or sentence that need to search
        :return: None
        """
        if words:
            words = words.decode('utf-8' if Linux else 'gbk')
        if level == 'warn':
            level = 'warning'

        if level:
            pattern = re.compile(r' \| %s \| ' % level.upper())
        elif words:
            if re.search(r'^\".*\"$', words):
                words = words[1:-1]
            pattern = re.compile(r'%s' % words)
        else:
            return

        self._log = [row for row in self._log if pattern.search(row)]

    def _follow(self, num):
        """ print appended log as the log grows

        :param num: the last num line
        :return: None
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
                if k in ['clear', 'follow', 'interact']:
                    checks.append(True)
                elif k in ['level', 'words', 'num', 'tag']:
                    checks.append(False)
        if len(set(checks)) > 1 or checks.count(True) > 1:
            print "%s: %s, %s, %s these options must use alone\n" % \
                  (("\033[1;31mError\033[0m", "\033[32m-i [--interact]\033[0m", "\033[32m-f [--follow]\033[0m",
                    "\033[32m-c [--clear]\033[0m")
                   if Linux else ("Error", "'-i [--interact]'", "'-f [--follow]'", "'-c [--clear]'"))
            return False
        else:
            return True

    def start(self, args):
        if self._check(args):
            with open(self._path) as rf:
                self._log = [row.decode('utf-8') for row in rf]
                for arg in list_remove_duplicate(sys.argv):
                    if arg.startswith('-n') or arg == '--num':
                        self._last(args.num)
                    elif arg.startswith('-t') or arg == '--tag':
                        self._tag()
                    elif arg.startswith('-l') or arg == '--level':
                        self._filter(level=args.level)
                    elif arg.startswith('-w') or arg == '--words':
                        self._filter(words=args.words)
                    elif arg.startswith('-c') or arg == '--clear':
                        self._clear()
                        return
                    elif arg.startswith('-f') or arg == '--follow':
                        self._follow(args.num)
                        return
                    elif arg.startswith('-i') or arg == '--interact':
                        InteractCmd(self._path).start()
                        return
                    else:
                        continue

                self._print()


class InteractCmd(Cmd):
    pattern_bat = re.compile(r'^ *((([hectvqrp])|(n +\d+)|(f( +\d+)?)|(l +(error|warn|warning|info|debug))|(w +(\S+|".+"|\'.+\'))) +)+$')
    pattern_per = re.compile(r'^n +\d+|f( +\d+)?|l +(error|warn|warning|info|debug)|w +(\S+|".+"|\'.+\')$')

    def __init__(self, path):
        super(InteractCmd, self).__init__(path)
        self._bak = None
        self._orders = OrderedDict()
        self._callback = {
            'p': self._print,
            'n': self._last,
            'l': self._filter,
            'w': self._filter,
            'e': self._empty,
            't': self._tag,
            'c': self._clear,
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
                4) Input \033[32mt\033[0m to print all tags of log
                5) Input \033[32mw WORDS\033[0m to filter out only the log line containing these words
                6) Input \033[32me\033[0m to empty all filter conditions
                7) Input \033[32mc\033[0m to empty the log file
                8) Input \033[32mr\033[0m to reload log file
                9) Input \033[32mf\033[0m to print appended log as the log grows                
               10) Input \033[32mv\033[0m to print using example
               11) Input \033[32mh\033[0m to print help menu
            """
        else:
            msg = """
                ###   Please select the following options   ### 
                
                0) Input 'q' to quit
                1) Input 'p' to print filtered log         
                2) Input 'n NUM' to filter out only the last n line of log
                3) Input 'l {debug,info,warn,warning,error}' to filter out only the log line containing this LEVEL
                4) Input 't' to print all tags of log
                5) Input 'w WORDS' to filter out only the log line containing these words
                6) Input 'e' to empty all filter conditions
                7) Input 'c' to empty the log file
                8) Input 'r' to reload log file
                9) Input 'f' to print appended log as the log grows                
               10) Input 'v' to print using example
               11) Input 'h' to print help menu                                
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
            if x in ['c', 'r', 'f', 'v', 'h', 'q']:
                checks.append(True)
            elif x in ['p', 'n', 'l', 't', 'e', 'w']:
                checks.append(False)
        if len(set(checks)) > 1 or checks.count(True) > 1:
            print "%s: %s, %s, %s, %s, %s, %s these options must use alone\n" % \
                  (("\033[1;31mError\033[0m", "\033[32mc\033[0m", "\033[32mr\033[0m", "\033[32mf\033[0m",
                    "\033[32mv\033[0m", "\033[32mh\033[0m", "\033[32mq\033[0m")
                   if Linux else ("Error", "'c'", "'r'", "'f'", "'v'", "'h'", "'q'"))
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
            elif k == 'w':
                self._callback[k](words=v)
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
