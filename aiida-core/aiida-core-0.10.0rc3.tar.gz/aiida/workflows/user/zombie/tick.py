
from aiida.work.daemon import tick_workflow_engine
from argparse import ArgumentParser
import sys
from time import sleep

if __name__ == '__main__':
    
	tick_workflow_engine()

    #parser = ArgumentParser()
    #parser.add_argument('-n', required=False, type=int, default=1)
    #parser.add_argument('-s', '--sleep', required=False, type=float, default=0)
    #parsed = parser.parse_args(sys.argv[1:])
    #for i in range(parsed.n):
    #    print "Ticking workflows"
    #    tick_workflow_engine()
    #    sleep(parsed.sleep)
