#!/usr/bin/env python

import os, sys

# add relative paths for imports
root_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, root_dir)

from leolabs.cli.utils import *
from leolabs.cli.commands import *

def main():

    load_config()

    parser = argparse.ArgumentParser(description='LeoLabs Command Line Interface')
    parser.add_argument('resource', nargs='?')
    parser.add_argument('command', nargs='?')
    parser.add_argument('--catalog-number', dest='catalog_number')
    parser.add_argument('--norad-catalog-number', dest='norad_catalog_number')
    parser.add_argument('--state', dest='state')
    parser.add_argument('--instrument', dest='instrument')
    parser.add_argument('--task', dest='task')
    parser.add_argument('--latest', dest='latest')
    parser.add_argument('--start-time', dest='start_time')
    parser.add_argument('--end-time', dest='end_time')
    parser.add_argument('--timestep', dest='timestep')
    args = parser.parse_args()

    commands = CommandList()
    commands.add(Command('configure', None, configure))
    commands.add(Command('catalog', 'list', catalog_list))
    commands.add(Command('catalog', 'get', catalog_get))
    commands.add(Command('catalog', 'get-statistics', catalog_get_statistics))
    commands.add(Command('catalog', 'get-measurements', catalog_get_measurements))
    commands.add(Command('catalog', 'get-planned-passes', catalog_planned_passes))
    commands.add(Command('catalog', 'list-states', catalog_list_states))
    commands.add(Command('catalog', 'get-state', catalog_get_state))
    commands.add(Command('catalog', 'get-propagation', catalog_get_propagation))
    commands.add(Command('catalog', 'create-task', catalog_create_task))
    commands.add(Command('instruments', 'list', instruments_list))
    commands.add(Command('instruments', 'get', instruments_get))
    commands.add(Command('instruments', 'list-tasks', instruments_list_tasks))
    commands.add(Command('instruments', 'create-task', instruments_create_task))
    commands.add(Command('instruments', 'get-task', instruments_get_task))
    commands.add(Command('instruments', 'get-task-measurements', instruments_get_task_measurements))
    commands.add(Command('instruments', 'get-statistics', instruments_get_statistics))
    
    try:
        return commands.invoke(args)
    except Exception as e:
        sys.stderr.write(repr(e) + '\n')
        sys.exit(1)

if __name__ == '__main__':
    main()