"""
Command-line utility for creating gptools from ENVI Tasks
"""
import argparse
import sys

# Python 3
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from envipyarc import GPToolbox
from envipyengine import Engine

parser = argparse.ArgumentParser(
    description='Creates an ESRI GPToolbox that wraps ENVI tasks.')
parser.add_argument('task_name', nargs='+', help='a list of task names to wrap as gptools')
parser.add_argument('--output', dest='output', help='the output file of the generated toolbox. Default is the service name')

args = parser.parse_args()

engine = Engine('ENVI')

tasks = []
for task_name in args.task_name:
    tasks.append(engine.task(task_name))

print('Initializing toolbox factory')
toolbox = GPToolbox(tasks)

output = args.output if args.output else 'ENVI'
print('Creating toolbox: ' + output)
toolbox.create_toolbox(output)

print('Finished')