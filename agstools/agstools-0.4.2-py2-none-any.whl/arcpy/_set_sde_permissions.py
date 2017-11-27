from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input, int, map, next, oct, open, pow,
                      range, round, str, super, zip)

import argparse
import os

from agstools._helpers import create_argument_groups, namespace_to_dict

def create_parser_setsdeperm(parser):
    parser.set_defaults(func = _execute_process_permissions_changes)
    
    parser.add_argument("-p", "--permissions", 
        help = "The absolute or relative path to the JSON-encoded permissions data.")
        
    parser.add_argument("-c", "--connection", 
        help = "The absolute or relative path to the SDE connection file.") 