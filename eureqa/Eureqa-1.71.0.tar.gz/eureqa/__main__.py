import sys

from collections import defaultdict

from .install_analysis_template import main as install_main
from .run_analysis_template import main as run_main

def error(args):
    print "Unrecognized command"

if len(sys.argv) < 2:
    error(sys.argv)

command = sys.argv[1]
remaining_args = [sys.argv[0]] + sys.argv[2:]
    
actions = defaultdict(lambda: error,
                      { 'run_analysis_template': run_main,
                        'install_analysis_template': install_main })

actions[command](remaining_args)
