#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

import sys
import os
import argcomplete
import argparse
import Cli

from dockerManager.Config import Config
from dockerManager.Container import Container
from dockerManager.plugins.Hosts import Hosts

bridgeName = 'docker0'
bridgeIpRange = '172.17.0.1/24'

interface = Cli.Interface()
command = Cli.Command()

if len(sys.argv) > 2:
    interface.error("Argument error - Only one parameter -action is needed!")
    sys.exit(1)

# create parser in order to autocomplete
parser = argparse.ArgumentParser()

parser.add_argument(
    'action',
    help = "Where is you desired config file?",
    type = str,
    choices = ['start', 'stop', 'restart'],
    default = 'start'
)

argcomplete.autocomplete(parser)

def main():
  arguments = parser.parse_args()
  action = arguments.action

  if action == 'start':
    interface.header("Starting network bridge")
    command.execute("brctl addbr %s" % (bridgeName))
    command.execute("ip addr add %s dev %s" % (bridgeIpRange, bridgeName))
    command.execute("ip link set dev %s up" % (bridgeName))

  sys.exit(0)
  
