__version__ = '0.6b22'

import argparse
import asyncio
import logging
import logging.config
import os
import shutil
import subprocess

import ws_storage.server
import ws_storage.impl.filesystem

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(__file__)

def runserver(args):
    try:
        ws_storage.server.runserver(args)
    except Exception as e:
        logger.exception(str(e))

def install(args):
    # copy systemd file
    shutil.copyfile(
            os.path.join(BASE_DIR, 'ws_storage.service'),
            os.path.join('/lib/systemd/system', 'ws_storage.service'))

    config_dir_dst = '/etc/ws_storage/conf'

    # make etc directory
    try:
        os.makedirs(config_dir_dst)
    except: pass
    
    # copy default config file
    shutil.copyfile(
            os.path.join(BASE_DIR, 'tests/conf/simple.py'),
            os.path.join(config_dir_dst, 'simple.py'))
    shutil.copyfile(
            os.path.join(BASE_DIR, 'tests/conf/simple_console.py'),
            os.path.join(config_dir_dst, 'simple_console.py'))

    p = subprocess.Popen(('systemctl', 'daemon-reload'))
    p.communicate()
    p = subprocess.Popen(('systemctl', 'restart', 'ws_storage.service'))
    p.communicate()

def main(argv):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
 
    def help_(_):
        parser.print_help()

    parser.set_defaults(func=help_)
   
    parser_runserver = subparsers.add_parser('runserver')
    parser_runserver.add_argument(
            '-d',
            action='store_true',
            help='develop mode',
            )
    parser_runserver.add_argument(
            '--conf_dir',
            default=None,
            help='modconf module directory',
            )
    parser_runserver.add_argument(
            'conf_mod',
            help='modconf module name',
            )
    parser_runserver.add_argument(
            '--impl',
            default=None,
            help='storage implementation',
            )
    parser_runserver.add_argument('--port', type=int)

    parser_runserver.set_defaults(func=runserver)
 
    parser_install = subparsers.add_parser('install')
    parser_install.set_defaults(func=install)

    args = parser.parse_args(argv[1:])
    args.func(vars(args))







