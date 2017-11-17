#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4 ft=python fenc=UTF-8 ai

'''
pcrunner.main
-------------

Main entry point for the pcrunner command.
'''

import argparse
import itertools
import logging
import logging.handlers
import os
import stat
import subprocess
import sys
import threading
import time
from glob import glob
from . import configuration
from . import __version__
from . daemon import Daemon
from . exception import PostFailed
from . exception import PostResultTooBig

PY3 = sys.version > '3'

if PY3:
    from queue import Queue
    from urllib.parse import urlencode
    from urllib.request import Request
    from urllib.request import urlopen
else:
    from Queue import Queue
    from urllib import urlencode
    from urllib2 import Request
    from urllib2 import urlopen

logger = logging.getLogger(__name__)


class PassiveCheckRunnerDaemon(Daemon):
    def __init__(self, pcrunner):
        self.pcrunner = pcrunner
        self.pid_file = pcrunner.pid_file

    def run(self):
        self.pcrunner.run()


class Check(object):
    def __init__(self, result_type, name, command, hostname):
        self.result_type = result_type
        self.name = name
        self.command = command
        self.hostname = hostname
        self.pid = None
        self.process = None
        self.returncode = 3
        self.terminated = False
        self.stdout = ''
        self.stderr = ''
        self.performance_data = ''
        self.starttime = 0
        self.endtime = 0

    def start(self):
        # should be called once
        assert self.endtime == 0
        self.starttime = time.time()

    def end(self):
        # should be called once
        assert self.endtime == 0
        self.endtime = time.time()

    def run(self):
        """
        Run the command and saves excection data
        """
        # Start the time
        self.start()
        logger.debug('check %s: started at %s', self.name, self.starttime)

        try:
            logger.debug('check %s: excecuting %s', self.name, self.command)
            if os.name == 'nt':
                cmd = self.command
            else:
                cmd = self.command.split()
            # Start process
            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError as error:
            self.end()
            self.returncode = 3
            self.stdout = ' '
            self.stderr = str(error)
            logger.error(
                'check %s: failed: duration: %.4f command: %s'
                'return code %d stdout: %s stderr: %s', self.name,
                self.duration, self.command, self.returncode, self.stdout,
                self.stderr)
        else:
            # Procces started
            self.pid = self.process.pid
            logger.debug('check %s: started with PID: %d', self.name, self.pid)

            # Wait for output
            stdout, stderr = self.process.communicate()

            # Procces ended, stop the time
            self.end()

            if self.terminated:
                # Time must have ran out
                # check got terminated
                self.returncode = 3
                self.stdout = ''
                self.stderr = 'terminated, max time reached'
                logger.error('check %s: %s ', self.name, self.stderr)
            else:
                self.returncode = self.process.returncode
                self.stdout = ' '.join(stdout.splitlines())
                self.stderr = ' '.join(stderr.splitlines())

                logger.debug(
                    'check %s: finished: PID: %d  return code %d',
                    self.name,
                    self.pid,
                    self.returncode
                )

    def terminate(self):
        """
        Terminates check if still running.
        """
        if self.pid is not None and self.endtime == 0:
            # Check started but not ended
            logger.debug(
                'check %s: terminated duration: %.4f PID: %d',
                self.name,
                self.duration,
                self.pid,
            )
            try:
                self.process.terminate()
            except OSError as error:
                logger.critical(
                    'check %d: termination failed PID %d error: %s',
                    self.name,
                    self.pid,
                    error,
                )
                logger.critical('Exiting main program now')
                sys.exit(3)
            else:
                self.terminated = True
        elif self.endtime:
            logger.debug(
                'check %s: already finished, not terminating: '
                'PID: %d return code %d',
                self.name,
                self.pid,
                self.returncode
            )
        else:
            logger.debug('check %s: not started, not terminating', self.name)

    @property
    def duration(self):
        return self.endtime - self.starttime

    @property
    def elapsed(self):
        return time.time() - self.starttime

    def __str__(self):
        '''
        String representation in NSCA format
        '''
        return '[{0:.0f}] {1};{2};{3};{4};{5}'.format(
            self.endtime,
            self.result_type,
            self.hostname,
            self.name,
            self.returncode,
            ' '.join(
                (self.stdout, self.stderr, self.performance_data)).strip(),
        )


class CheckRun(object):
    def __init__(self, hostname):
        self.hostname = hostname


class PassiveCheckRunner(object):
    def __init__(self, nsca_web_url, nsca_web_username, nsca_web_password,
                 hostname, command_file, result_file, result_dir,
                 max_procs, interval, lines_per_post, pid_file, http_timeout,
                 max_line_size):
        self.nsca_web_url = nsca_web_url
        self.nsca_web_username = nsca_web_username
        self.nsca_web_password = nsca_web_password
        self.hostname = hostname
        self.command_file = command_file
        self.result_file = result_file
        self.result_dir = result_dir
        self.max_procs = max_procs
        self.interval = interval
        self.lines_per_post = lines_per_post
        self.pid_file = pid_file
        self.http_timeout = http_timeout
        self.max_line_size = max_line_size
        self.timeout = self.interval - 10
        self.check_pcrunner = Check(
            'PROCESS_SERVICE_CHECK_RESULT',
            'pcrunner',
            'pcrunner',
            self.hostname,
        )
        # Get commands
        self.check_command_list = \
            configuration.read_check_commands(self.command_file)

    def __str__(self):
        mesg = '<pcrunner nsca_web_url: {0} nsca_web_username: {1}'
        mesg += ' hostname: {2} command_file: {3} result_file: {4}'
        mesg += ' max_procs:{5} timeout:{6} interval:{7} lines_per_post:{8}>'
        return mesg.format(
            self.nsca_web_url,
            self.nsca_web_username,
            self.hostname,
            self.command_file,
            self.result_file,
            self.max_procs,
            self.timeout,
            self.interval,
            self.lines_per_post,
        )

    def get_checks(self):
        self.checks = []
        for args in self.check_command_list:
            args['hostname'] = self.hostname
            self.checks.append(Check(**args))
        self.number_of_checks = len(self.checks)

    def kill_running_checks(self):
        # don't block if start_queue is empty
        if self.start_queue is not None or not self.start_queue.empty():
            # Remove checks that not got started from start_queue.
            # Put on temperary list to get start_queue empty a.s.a.p.
            while True:
                # Get all checks from start_queue unit we hit a None
                check = self.start_queue.get()
                if check is None:
                    # Put 'None' that got just removed on the queue again
                    # to make all threads end
                    self.start_queue.put(None)
                    break
                self.checks_not_started.append(check)

        self.number_of_checks_not_started = len(self.checks_not_started)

        # Kill running checks.
        while not self.run_queue.empty():
            check = self.run_queue.get()
            logger.debug('check %s: terminate', check.name)
            check.terminate()
            if check.terminated:
                logger.debug('check %s: terminated', check.name)
                self.number_of_checks_terminated += 1
            logger.debug('check %s: on finished queue', check.name)
        logger.error('%d checks terminated', self.number_of_checks_terminated)

        # Write returncode and stderr for checks that did not start.
        for check in self.checks_not_started:
            check.start()
            check.end()
            check.returncode = 3
            check.stdout = ''
            check.stderr = 'check not started, max time exceeded'
            # Move check result queue.
            self.finished_queue.put(check)
            logger.debug('check %s: on finished queue', check.name)
            logger.error(check.stderr)
        logger.error('%d checks not started',
                     self.number_of_checks_not_started)

    def check_results_from_finished_queue(self):
        self.current_check_results = []
        while not self.finished_queue.empty():
            check = self.finished_queue.get()
            logger.debug('format check result: %s', check)
            self.current_check_results.append('{0}\n'.format(check))

    def post(self, lines):
        results = ''.join(lines)
        number_of_lines = len(lines)
        if len(results) > self.lines_per_post * self.max_line_size:
            raise PostResultTooBig
        values = {
            'username': self.nsca_web_username,
            'password': self.nsca_web_password,
            'input': results,
        }
        data = urlencode(values)
        data_len = len(data)
        headers = {
            'User-Agent': 'pcrunner',
            'Content-length': data_len,
            'Content-type': 'application/x-www-form-urlencoded',
        }
        request = Request(self.nsca_web_url, data, headers)
        try:
            logger.debug('Posting %d results to: %s with length %d.',
                         number_of_lines, self.nsca_web_url, data_len)
            response = urlopen(request, timeout=self.http_timeout)
        except Exception as error:
            logger.error('Failed to post %d results to %s: %s',
                         number_of_lines, self.nsca_web_url, error)
            raise PostFailed
        else:
            http_response_code = response.getcode()
            logger.debug('HTTP return code: %s', http_response_code)
            if http_response_code != 200:
                logger.error('HTTP return code: %s', http_response_code)
                raise PostFailed

    def post_results_previous_run(self):
        '''
        If a previous result file exists post the results that are found in
        this file in chunks of number of lines per post.  If post fails save
        failed checks in ``self.results_post_failed``.
        '''
        try:
            with open(self.result_file) as fd:
                # There are results which are not posted in previous run.
                # Try post them.
                logger.debug('result file %s exists, try post old results',
                             self.result_file)
                # Iterate through result file.
                # Post lines_per_post>
                while True:
                    lines = list(itertools.islice(fd, self.lines_per_post))
                    if not lines:
                        break
                    try:
                        self.post(lines)
                    except PostFailed:
                        self.results_post_failed += lines
                        # Get rest of the lines
                        self.results_post_failed += list(
                            itertools.islice(fd, None))
                        logger.debug(
                            '%d lines of old check results saved for later'
                            ' posting',
                            len(self.results_post_failed)
                        )
                        break
            # Remove current result file.
            # failed results are saved in self.results_post_failed
            logger.debug('remove current result file: %s', self.result_file)
            try:
                os.remove(self.result_file)
            except OSError as error:
                logger.error(error)

        except IOError:
            # There is no result file: no old results to post.
            logger.debug(
                'No result file (%s) of previous run.',
                self.result_file
            )

    def read_results_from_spool_dir(self):
        if self.result_dir:
            logger.debug(
                'reading results files from spool direcotry %s',
                self.result_dir
            )
            epoch_time_fmt = 10 * '[0-9]'
            result_files = glob(
                '{0}/{1}*'.format(self.result_dir, epoch_time_fmt)
            )
            for result_file in result_files:
                with open(result_file, 'r') as fd:
                    logger.debug('reading results from %s', result_file)
                    for line in fd.readlines():
                        if len(line) < self.max_line_size:
                            self.check_results_external_commands.append(line)
                        else:
                            logger.warning(
                                'line in result file {0} exceeds max length '
                                'of {1})',
                                result_file,
                                self.max_line_size
                            )
                try:
                    os.remove(result_file)
                    logger.debug('deleting %s', result_file)
                except OSError as error:
                    logger.error(error)

        else:
            logger.debug('No result directory configured: not reading results'
                         ' from external commands.')

    def write_failed_results(self):
        logger.debug(
            'Saving %d results to file: %s',
            len(self.results_post_failed),
            self.result_file,
        )
        try:
            with open(self.result_file, 'w') as fd:
                fd.write(''.join(self.results_post_failed))
        except Exception as error:
            logger.error(error)

    def post_results(self):
        self.results_post_failed = []
        check_results = []
        # If there is a previous result file post it
        self.post_results_previous_run()
        # Get results from external commands
        self.read_results_from_spool_dir()
        # Combine and sort results from current and external commands
        check_results = self.current_check_results + \
            self.check_results_external_commands
        # make sure it's sorted
        check_results.sort()
        # Save to file if (post_results_previous_run) already failed
        if self.results_post_failed:
            # Already post failed
            # Add current results and write to file for next time posting
            self.results_post_failed += check_results
            self.write_failed_results()
        else:
            # No previous posting or succesfull posting.
            # Post external command and current results.
            check_results_iter = iter(check_results)
            while True:
                lines = list(
                    itertools.islice(check_results_iter, self.lines_per_post)
                )
                if not lines:
                    break
                try:
                    self.post(lines)
                except PostFailed:
                    self.results_post_failed += lines
                    # Get rest of the lines
                    self.results_post_failed += list(
                        itertools.islice(check_results_iter, None)
                    )
                    logger.debug(
                        '%d lines of check results saved for later'
                        ' posting',
                        len(self.results_post_failed)
                    )
                    break
            if self.results_post_failed:
                self.write_failed_results()

    @property
    def number_of_checks_finished(self):
        return (self.number_of_checks - self.number_of_checks_terminated -
                self.number_of_checks_not_started)

    def check_pcrunner_end(self):
        # All checks finished
        self.check_pcrunner.end()
        logger.debug('finished at at %.4f', self.check_pcrunner.endtime)
        logger.debug('total duration: %.4f seconds',
                     self.check_pcrunner.duration)

        exit_value = ('OK', 'WARNING', 'CRITICAL', 'UNKNOWN')

        self.check_pcrunner.performance_data = '| duration={0:f}, ' \
            'finished={1:d}, terminated={2:d}, not_started={3:d}'.format(
                self.check_pcrunner.duration,
                self.number_of_checks_finished,
                self.number_of_checks_terminated,
                self.number_of_checks_not_started,
            )

        self.check_pcrunner.stdout = '{0} total time: {1:.4f} sec'.format(
            exit_value[self.check_pcrunner.returncode],
            self.check_pcrunner.duration,
        )
        logger.debug(self.check_pcrunner)
        # Add pcrunner's own result
        self.finished_queue.put(self.check_pcrunner)
        # Get results
        self.check_results_from_finished_queue()
        # Post results
        self.post_results()
        return (
            self.check_pcrunner.returncode,
            ' '.join(
                (
                    self.check_pcrunner.stdout,
                    self.check_pcrunner.stderr,
                    self.check_pcrunner.performance_data
                )
            )
        )

    def start(self):
        '''
        Get checks, put them on start_queue and start threads.
        When max time reached kill all running processes.
        '''
        self.number_of_checks_terminated = 0
        # start new check_pcrunner check
        self.check_pcrunner = Check(
            'PROCESS_SERVICE_CHECK_RESULT',
            'pcrunner',
            'pcrunner',
            self.hostname,
        )

        # pcrunner is a check too (but does (should) not use self.run())
        self.check_pcrunner.start()

        # List of checks to be filled by self.get_checks()
        self.checks_not_started = []
        self.number_of_checks_not_started = 0
        self.current_check_results = []
        self.check_results_external_commands = []

        # Make queues
        self.start_queue = Queue()
        self.run_queue = Queue()
        self.finished_queue = Queue()

        # Get checks
        self.get_checks()

        # with no Checks here something got wrong.
        if self.number_of_checks == 0:
            self.check_pcrunner.stderr = ' '.join(
                [self.check_pcrunner.stderr, 'start_queue empty']
            )
            logger.critical(self.check_pcrunner.stderr)
            self.check_pcrunner.end()
            return (
                self.check_pcrunner.returncode,
                ' '.join(
                    (self.check_pcrunner.stdout, self.check_pcrunner.stderr)
                )
            )
        else:
            logger.debug('putting %d checks on start_queue',
                         self.number_of_checks)
        # Fill start_queue
        for check in self.checks:
            self.start_queue.put(check)

        # Put 'None's at the end of the start_queue
        # to signal thread funtion to stop.
        for i in range(self.max_procs):
            self.start_queue.put(None)

        # Start threads
        threads = [
            threading.Thread(
                target=run_process,
                args=(self.start_queue, self.run_queue, self.finished_queue)
            )
            for x in range(self.max_procs)
        ]

        for t in threads:
            t.daemon = False
            t.start()

        while self.finished_queue.qsize() < self.number_of_checks:
            # There are still results to be captured
            time.sleep(.5)

            logger.debug(
                'start queue: %d, run queue: %d, finished queue: %d, '
                'time elapsed: %.2f sec, timeout: %d ',
                self.start_queue.qsize(),
                self.run_queue.qsize(),
                self.finished_queue.qsize(),
                self.check_pcrunner.elapsed,
                self.timeout,
            )

            if self.check_pcrunner.elapsed > self.timeout:
                # Running out of time!
                msg = 'timeout at {0:.2f} sec'.format(
                    self.check_pcrunner.elapsed)
                logger.error(msg)
                self.check_pcrunner.stderr = ' '.join(
                    [self.check_pcrunner.stderr, msg])

                # Kill running checks
                self.kill_running_checks()

        # Only warn 'self check' for now
        if self.number_of_checks_finished == self.number_of_checks:
            self.check_pcrunner.returncode = 0
        else:
            self.check_pcrunner.returncode = 1
        return self.check_pcrunner_end()

    def stop(self):
        logger.warning('stop initiated')
        self.kill_running_checks()
        logger.warning('stopped')
        return self.check_pcrunner_end()

    def run(self):
        while True:
            self.start()
            time.sleep(self.interval)


def run_process(start_queue, run_queue, finished_queue):
    '''
    Function to be started as thread.
    Runs checks from start_queue, puts them on end_queue
    '''
    while True:
        # Get command from start_queue
        check = start_queue.get()
        if check is None:
            logger.debug('no more checks on start queue')
            break
        # There are checks to run
        run_queue.put(check)
        logger.debug('check %s: on run queue', check.name)
        # Run check
        check.run()
        logger.debug('check %s: on finished queue', check.name)
        finished_queue.put(check)


def slice_up_file(fd, number_of_lines):
    '''
    return lists
    '''
    pass


def is_socket(path):
    return os.path.exists(path) and \
        stat.S_ISSOCK(os.stat(path).st_mode)


def get_syslog_socket_or_win32():
    LINUX2_SYSLOG_SOCKET = '/dev/log'
    DARWIN_SYSLOG_SOCKET = '/var/run/syslog'
    if sys.platform == 'linux2' and is_socket(LINUX2_SYSLOG_SOCKET):
        return LINUX2_SYSLOG_SOCKET
    elif sys.platform == 'darwin' and is_socket(DARWIN_SYSLOG_SOCKET):
        return DARWIN_SYSLOG_SOCKET
    else:
        # Windows
        return None


def setup_logging(log_file=None, verbose=False):
    if verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    log_format = logging.Formatter(
        fmt='%(asctime)s %(name)s [%(process)d] %(levelname)-8s %(message)s',
        datefmt='%b %d %H:%M:%S',
    )

    if log_file:
        # File Handler
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            mode='a',
            maxBytes=4194304,
            backupCount=4,
        )
        handler.setFormatter(log_format)
    else:
        # Console Handler
        handler = logging.StreamHandler()
        handler.setFormatter(log_format)

    handler.setLevel(log_level)

    # Add to root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)


def remove_root_logger_handlers():
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.close()
    root_logger.handlers = []


def setup_syslog_with_config_opts(log_file, verbose, syslog_server,
                                  syslog_port):
    # remove existing handlers
    remove_root_logger_handlers()

    if log_file or verbose:
        # Log only to file
        setup_logging(log_file, verbose)

    else:
        # No debug to syslog (seems not to work anyway)
        log_level = logging.INFO

        if syslog_server:
            # use remote syslog server
            syslog_address = (syslog_server, syslog_port)
        else:
            # get_socket_address
            syslog_address = get_syslog_socket_or_win32()

        if syslog_address:
            # Syslog handler
            handler = logging.handlers.SysLogHandler(syslog_address)
            handler.setFormatter(
                logging.Formatter(
                    fmt='%(name)s [%(process)d]: %(message)s',
                    datefmt=None,
                )
            )
        elif sys.platform == 'win32':
            handler = logging.handlers.NTEventLogHandler('pcrunner')
        else:
            # Console handler
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter(
                    fmt='%(asctime)s %(name)s [%(process)d] %(levelname)-8s '
                        '%(message)s',
                    datefmt='%b %d %H:%M:%S',
                )
            )

        handler.setLevel(log_level)

        # Add to root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(handler)


def parse_pcrunner_args(args):
    '''
    Parse the command-line arguments to pcrunner.
    '''
    parser = argparse.ArgumentParser(
        prog='pcrunner',
        description='Passive Command Runner.',
    )
    parser.add_argument(
        '-c',
        '--config-file',
        help='Configuration file',
    )
    parser.add_argument(
        '-n',
        '--nsca_web_url',
        help='NSCA server url.',
    )
    parser.add_argument(
        '-u',
        '--nsca-web-username',
        help='NSCA Web username.',
    )
    parser.add_argument(
        '-p',
        '--nsca-web-password',
        help='NSCA Web password.',
    )
    parser.add_argument(
        '-o',
        '--command-file',
        help='Command file.',
    )
    parser.add_argument(
        '-H',
        '--hostname',
        help='Hostname excpected by Nagios/Icinga.',
    )
    parser.add_argument(
        '-i',
        '--interval',
        type=int,
        help='Time interval between checks in seconds.',
    )
    parser.add_argument(
        '-m',
        '--max-procs',
        type=int,
        help='Max processes to run simultaneously.',
    )
    parser.add_argument(
        '-e',
        '--lines-per-post',
        type=int,
        help='number of lines per HTTP post',
    )
    parser.add_argument(
        '-r',
        '--result-file',
        help='File to where results are written to when NSCA webserver is not '
        'reachable.',
    )
    parser.add_argument(
        '-d',
        '--result-dir',
        help='Directory for results from external commands.',
    )
    parser.add_argument(
        '-f',
        '--pid-file',
        help='PID file',
    )
    parser.add_argument(
        '-t',
        '--http-timeout',
        type=int,
        help='Max secs to timeout when posting results to NSCA webserver',
    )
    parser.add_argument(
        '-s',
        '--max-line-size',
        type=int,
        help='Maximum result data to post to NSCA webserver in bytes per'
        ' line.'
    )
    parser.add_argument(
        '-l',
        '--log-file',
        help='log file',
    )
    # start /stop daemon arguments
    parser.add_argument(
        'runloop',
        choices=('start', 'stop'),
        nargs='?',
        help='Start or stop %(prog)s runloop',
    )
    parser.add_argument(
        '-a',
        '--no-daemon',
        action='store_true',
        help='Run %(prog)s in foreground'
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Show verbose info (level DEBUG).',
    )
    parser.add_argument(
        '--version',
        action='store_true',
        help='Show version',
    )
    return parser.parse_args(args)


def main():
    '''
    Entry point for the package, as defined in setup.py.
    '''
    # Parse args
    args = parse_pcrunner_args(sys.argv[1:])

    # Version info
    if args.version:
        print(__version__)
        sys.exit(0)

    # Setup basic logging
    setup_logging(args.log_file, args.verbose)

    # Get configuration
    config = configuration.Config(vars(args))

    logger.debug('Configuration:')
    for key, value in config.items():
        logger.debug('%-20s:%s', key, value)

    # Get logging args
    log_args = config.subset('log_file', 'verbose', 'syslog_server',
                             'syslog_port')
    # Logging with config opts
    setup_syslog_with_config_opts(**log_args)

    # Get PassiveCheckRunner args
    pcrunner_args = config.subset('nsca_web_url', 'nsca_web_username',
                                  'nsca_web_password', 'hostname',
                                  'command_file', 'result_file', 'result_dir',
                                  'max_procs', 'interval', 'lines_per_post',
                                  'pid_file', 'http_timeout', 'max_line_size')

    # Init Passive Check Runner
    pcrunner = PassiveCheckRunner(**pcrunner_args)

    logger.info('Initialize Passive Check Runner: %s', pcrunner)

    if args.runloop:
        if os.name == 'posix':
            if args.no_daemon is False:
                daemon = PassiveCheckRunnerDaemon(pcrunner)
            if args.runloop == 'start':
                if args.no_daemon is True:
                    pcrunner.run()
                else:
                    return daemon.start()
            elif args.runloop == 'stop':
                if args.no_daemon is True:
                    raise NotImplementedError
                else:
                    return daemon.stop()
        else:
            logger.error(
                'Running as daemon on implemented on Posix systems. '
                'See windows_service.py for running Passive Check Runner '
                'under Windows as a Service.'
            )
    else:
        # run once
        return pcrunner.start()


if __name__ == '__main__':
    main()
