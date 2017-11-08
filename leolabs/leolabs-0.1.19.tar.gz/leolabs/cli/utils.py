import os, sys
import traceback
from collections import defaultdict
import argparse
import json
import requests

access_key = None
secret_key = None
override_base_uri = None

def quit(message):
    sys.stderr.write(message + '\n')
    sys.exit(1)

def prompt(s):
  if sys.version_info[0] < 3:
    return raw_input(s)
  else:
    return input(s)

def api_request(resource, data=None, params=None):

    require_credentials()

    global override_base_uri
    if not override_base_uri:
        base_uri = 'https://api.leolabs.space/v1'
    else:
        base_uri = override_base_uri

    uri = base_uri + resource

    headers = {
        'Authorization': 'basic {0}:{1}'.format(access_key, secret_key)
    }

    for retry in range(5):
        if data is None:
            response = requests.get(uri, headers=headers, params=params)
        else:
            response = requests.post(uri, headers=headers, data=data)

        if response.status_code >= 200 and response.status_code <= 399:
            return response.json()

    sys.stderr.write('Request failed with code {0} after retries: "{1}"\n'.format(response.status_code, uri))
    try:
        return response.json()
    except:
        return {'error': 'unknown'}

class Command:
    def __init__(self, resource, command, function):
        self.resource = resource
        self.command = command
        self.function = function

    def invoke(self, args):
        result = self.function(**vars(args))
        if result:
            print(json.dumps(result, indent=4))
        return 0

class CommandList:
    def __init__(self):
        self.commands = defaultdict(defaultdict)

    def add(self, command):
        self.commands[command.resource][command.command] = command

    def invoke(self, args):
        resource = args.resource
        command = args.command

        if resource not in self.commands:
            sys.stderr.write('Did not recognize resource: "{0}", valid choices are: {1}\n'.format(resource if resource else '', self.commands.keys()))
            sys.exit(1)

        if command not in self.commands[resource]:
            sys.stderr.write('Did not recognize command "{0}" for resource "{1}", valid choices are: {2}\n'.format(command if command else '', resource, self.commands[resource].keys()))
            sys.exit(1)

        return self.commands[resource][command].invoke(args)

def import_configparser():
    """ Python 2 + 3 compatibility bridge """
    if sys.version_info[0] < 3:
      import ConfigParser
      configparser = ConfigParser
    else:
      import configparser
    return configparser

def load_config():

    global access_key, secret_key, override_base_uri

    if access_key and secret_key:
        return

    access_key = os.environ.get('LEOLABS_ACCESS_KEY')
    secret_key = os.environ.get('LEOLABS_SECRET_KEY')
    override_base_uri = os.environ.get('LEOLABS_BASE_URI')

    if access_key and secret_key:
        return

    configparser = import_configparser()

    from os.path import expanduser
    home_dir = expanduser("~")
    leolabs_dir = os.path.join(home_dir, '.leolabs')
    config_path = os.path.join(leolabs_dir, 'config')

    try:
        config = configparser.ConfigParser()
        config.read(config_path)
        access_key = config.get('credentials', 'access_key')
        secret_key = config.get('credentials', 'secret_key')
        override_base_uri = config.get('default', 'base_uri')

        if access_key and secret_key:
            return
    except:
        pass


def require_credentials():    
    if not access_key or not secret_key:
        quit('Missing LeoLabs credentials. Please set the LEOLABS_ACCESS_KEY and LEOLABS_SECRET_KEY environment variables, or run "leolabs configure".')
