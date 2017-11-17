'''Demo Job File

This is an example jobfile, intended to show how job files work, how they should
be written, what are the various things to write in it, and how each task is 
launched.

This jobfiles runs "demo_params.py" testscript file.

Run this jobfile in Easypy:
    
    # straightforward run (require testbed)
    bash$ easypy demo_job.py -testbed_file demo_tb.yaml

    # add some arguments and invoke jobfile parser
    bash$ easypy demo_job.py -testbed_file demo_tb.yaml --cli "show hardware" 

    # use more arguments: invoke pdb on fail
    bash$ easypy demo_job.py -pdb  -testbed_file demo_tb.yaml \
                             --cli "show does not exist" 
'''

import os
import logging
import argparse

from ats.easypy import run

here = os.path.dirname(__file__)

# easypy allows argument propagations
# any unrecognized is left behind to allow custom parsers to handle
parser = argparse.ArgumentParser()
parser.add_argument('--cli', dest = 'cli', 
                    type = str,
                    default = 'show running-config')

# main() function defines the entry point of each job file
def main():

    # do the parsing
    args = parser.parse_known_args()[0]

    # this is a great place to configure your log outputs
    logging.getLogger('ats.connections').setLevel('DEBUG')

    # run the previous parameters demo script
    run(testscript = os.path.join(here, 'demo_params.py'),
        cli = args.cli)

