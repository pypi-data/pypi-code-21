import sys
from forrest.commands import run

def cli():
  command = sys.argv[1]

  if command == 'run':
    run.process(sys.argv[2:])

