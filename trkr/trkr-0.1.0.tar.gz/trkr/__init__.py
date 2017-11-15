'''
Usage:
  trkr <command>

Commands:
  run             Runs the tracker
  setup           Launches the setup script
  help            Displays this message
'''

import sys

from trkr.commands.run import main as run
from trkr.commands.setup import main as setup

def main():
  if len(sys.argv) > 1:
    method = globals().get(sys.argv[1])
    if not method:
      print(__doc__)
    else:
      method()
  else:
    run()
