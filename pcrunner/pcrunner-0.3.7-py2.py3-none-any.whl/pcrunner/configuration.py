#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4 ft=python fenc=UTF-8 ai

'''
pcrunner.configuration
----------------------

Global configuration handling
'''

import logging
import multiprocessing
import os
import socket
import tempfile
import yaml


logger = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

TEMP_DIR = tempfile.gettempdir()

# PID file
if os.name == 'posix' and os.geteuid() == 0:
    PID_FILE = '/var/run/pcrunner.pid'
else:
    PID_FILE = os.path.join(TEMP_DIR, 'pcrunner.pid')

# Config
DEFAULT_CONFIG = {

    # NSCW Web url
    'nsca_web_url': 'http://localhost:5668/queue',

    # NSCW Web username
    'nsca_web_username': 'default',

    # NSCW Web password
    'nsca_web_password': 'changeme',

    # hostname of local host (host that is being checked)
    'hostname': socket.gethostname(),

    # log file, if configured don't use syslog
    'log_file': None,

    # Verbose logging
    'verbose': False,

    # File with check commands
    'command_file': os.path.join(BASE_DIR, 'etc', 'commands.yml'),

    # Directory for results from external commands (not activated by default)
    'result_dir': None,

    # Temp file for results not yet uploaded to NSCA Web
    'result_file': os.path.join(BASE_DIR, 'data', 'pcrunner.dat'),

    # Number of maximum process to run concurrent
    'max_procs': multiprocessing.cpu_count(),

    # Time interval between chekcs in seconds
    'interval': 60,

    # Max secs to timeout when posting results to NSCA webserver
    'http_timeout': 3,

    # FQDN Syslog server
    # or None for local socket
    'syslog_server': None,

    # Syslog server port
    'syslog_port': 514,

    # Number of lines per HTTP post
    'lines_per_post': 400,

    # Maximum result data to post to NSCA webserver in bytes per line.
    'max_line_size': 8192,

    # Pid file
    'pid_file': PID_FILE,
}

DEFAULT_NT_CONFIG = {
    # Configuration file
    'config_file': os.path.join(BASE_DIR, 'etc', 'pcrunner.yml'),
    # File with check commands
    'command_file': os.path.join(BASE_DIR, 'etc', 'commands.yml'),
    # File with check commands
    # 'log_file': os.path.join(BASE_DIR, 'log', 'pcrunner.log'),
}

DEFAULT_POSIX_CONFIG = {
    # Configuration file
    'config_file': '/etc/pcrunner/pcrunner.yml',
    # File with check commands
    'command_file': '/etc/pcrunner/commands.yml',
    # Temp file for results not yet uploaded to NSCA Web
    'result_file': '/var/spool/pcrunner/pcrunner.dat',
}

if os.name == 'nt':
    DEFAULT_CONFIG.update(DEFAULT_NT_CONFIG)
else:
    DEFAULT_CONFIG.update(DEFAULT_POSIX_CONFIG)


class Config(dict):
    def __init__(self, args=None, **kwargs):
        data = {}
        data.update(DEFAULT_CONFIG)
        if args is not None:
            logger.debug('Got arguments: %s', args)
            for key, value in args.items():
                if value:
                    data[key] = value
        if len(kwargs):
            data.update(kwargs)
        super(Config, self).__init__(data)
        self.update_yaml()

    def subset(self, *keys, **kwargs):
        '''
        Return a sub set of Config dict of *keys
        if kwargs also update the returned dictionary.
        '''
        _dict = dict((key, self.get(key)) for key in keys)
        if len(kwargs):
            _dict.update(kwargs)
        return _dict

    def update_yaml(self):
        '''
        Read Yaml config
        '''
        # Get defaults
        yaml_dict = {}
        try:
            with open(self['config_file']) as fd:
                try:
                    yaml_dict = yaml.safe_load(fd)
                except yaml.scanner.ScannerError:
                    logger.error('Not a valid YAML file: %s',
                                 self['config_file'])
        except IOError:
            logger.warning(
                "Can't open config file: %s using defaults"
                " and or command line arguments", self['config_file'])
        if yaml_dict:
            self.update(yaml_dict)


def read_check_commands_txt(fd):
    check_command_list = []
    command_txt = fd.read()
    check_command_list = [
        {
            'result_type': 'PROCESS_{0}_CHECK_RESULT'.format(y[0]),
            'name': y[1],
            'command': ' '.join(y[2:])
        } for y in (x.split('|') for x in command_txt.splitlines() if x)
    ]
    return check_command_list


def read_check_commands_yaml(fd):
    check_command_list = []
    try:
        check_command_list = yaml.safe_load(fd)
    except yaml.scanner.ScannerError:
        logger.error('Invalid YAML in command file.')
    return check_command_list


def read_check_commands(command_filename):
    check_command_list = []
    file_name, file_extention = os.path.splitext(command_filename)
    try:
        with open(command_filename, 'r') as fd:
            if file_extention == '.txt':
                check_command_list = read_check_commands_txt(fd)
            else:
                check_command_list = read_check_commands_yaml(fd)
    except IOError as err:
        logger.error(str(err))
    return check_command_list
