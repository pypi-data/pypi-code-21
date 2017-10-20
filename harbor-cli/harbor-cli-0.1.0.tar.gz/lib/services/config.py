'''
Harbor allows for a configuration files called harborConfig.json
usually for managing plugins supplied out of the box.
This module has methods to parse the config file, and additional plugin
specific helpers.
'''
import os

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
    options = get()
    if 'hipchat' not in options:
        return False
    return True
