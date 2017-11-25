'''
Harbor allows for a configuration files called harborConfig.json
usually for managing plugins supplied out of the box.
This module has methods to parse the config file, and additional plugin
specific helpers.
'''
import os

from lib.logger import logger
from lib.utils.json_parser import json_parse
from lib.exceptions.FileNotFound import FileNotFoundException

DEFAULT_CONFIG_PATH = os.getcwd() + '/harborConfig.json'

def get(configpath=DEFAULT_CONFIG_PATH):
    ''' Gets the config file details. '''
    if not exists(configpath):
        raise FileNotFoundException(
            configpath,
            'Configuration file not found.'
        )
    return json_parse(configpath)


def exists(configpath=DEFAULT_CONFIG_PATH):
    ''' Returns a bool indicating whther the config file exists. '''
    return os.path.isfile(configpath)


def is_hipchat_configured():
    '''
    Returns true if config object has a hipchat property
    '''
    if not exists():
        return False

    if not is_hipchat_config_valid():
        return False

    return True

def is_hipchat_config_valid():
    ''' Checks if hipchat is correctly configured. '''
    keys = ['company_name', 'room_id', 'auth_token']
    error = 'HipChat configuration found, but keys {keys} are missing.'

    if 'hipchat' not in get():
        return False

    config = get()
    hipchat = config['hipchat']

    missingkeys = []
    for key in keys:
        if key not in hipchat:
            missingkeys.append(key)

    if missingkeys:
        keyerror = error.format(keys=missingkeys)
        logger().error(keyerror)

        return False

    return True
