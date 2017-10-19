#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

import sys
import os
import argcomplete
import argparse
import Cli

from dockerManager.Config import Config
from dockerManager.Hosts import Hosts
from dockerManager.Nginx import Nginx
from dockerManager.BasicAuth import BasicAuth
from dockerManager.Container import Container
from dockerManager.Header import Header

interface = Cli.Interface()
if not os.path.isfile('.docker-manager'):
    interface.error('No .docker-manager file found in this directory!')
    sys.exit(1)

config = Config('.docker-manager')
config.load()

if len(sys.argv) == 2:
    # default branch name is *
    sys.argv.append('all-container')

# create parser in order to autocomplete
parser = argparse.ArgumentParser()

parser.add_argument(
    'command',
    help = "What command do you want to execute?",
    type = str,
    choices = [
        "status",
        "start",
        "stop",
        "update",
        "restart",
        "destroy"
    ]
)

parser.add_argument(
    'name',
    help = 'Which container you want to execute the command on?',
    choices = config.getContainerNames(True),
    type = str
)


argcomplete.autocomplete(parser)

def dispatch(command, name):
  settings = config.getContainerSettings(name)

  for i in range(0, settings['maxContainers']):

    containerName = "%s-%s" % (name, i)
    container = Container(containerName, settings)

    result = False
    try:
      # call container
      methodToCall = getattr(container, command)
      result = methodToCall()

      # call hosts
      hosts = Hosts(container)
      methodToCall = getattr(hosts, command)
      result = methodToCall()


    except Exception as e:
      interface.error(e)
      raise e

  if 'nginx' in settings and settings['nginx']:
    nginx = Nginx(name, settings)
    methodToCall = getattr(nginx, command)
    result = methodToCall()

    basicAuth = BasicAuth(name, settings)
    methodToCall = getattr(basicAuth, command)
    result = methodToCall()

def main():
  arguments = parser.parse_args()
  name = arguments.name
  command = arguments.command
  try:
    header = Header()
    headerToCall = getattr(header, command)
    result = headerToCall()
  except Exception as e:
    pass

  if name == 'all-container':
    names =  config.getContainerNames()
    for name in names:
      dispatch(command, name)
  else:
    dispatch(command, name)

  sys.exit(0)
  
