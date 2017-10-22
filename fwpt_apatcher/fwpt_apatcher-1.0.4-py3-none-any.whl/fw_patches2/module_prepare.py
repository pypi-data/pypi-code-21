'''
Created on 30.08.2011

@author: raidan
'''
from fw_patches2 import tools
from fw_patches2.Prepare import PatchPrepare
from optparse import OptionParser

def impl():
    # don't forget, sys.argv[0] is the python file with this script
    
    parser = OptionParser()
    parser.add_option("--root", dest="root", default="..",
                      help="Root directory for execute")
    parser.add_option("--out", dest="out", 
                      help="Output directory")   
    parser.add_option("--template", dest="template", 
                      help="Template directory")
    parser.add_option("--execute", dest="execute", 
                      help="Execute command")
    
    (options, _) = parser.parse_args()

     
    PatchPrepare(options.root).prepare(options.template, options.execute, options.out)

def prepare():
    tools.execute(impl)

if __name__ == '__main__':
    prepare()
