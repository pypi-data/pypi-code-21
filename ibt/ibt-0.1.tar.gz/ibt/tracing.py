###############################################################################
#
# IBT: Isolated Build Tool
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# Simple wrappers around Docker etc. for fully isolated build environments
#
###############################################################################

from __future__ import print_function
import colorama
import json

def _trace(s):
    print(colorama.Fore.YELLOW + s + colorama.Style.RESET_ALL)

def trace_command(args, command):
    if args.verbose:
        _trace(args, shell_join(command))

def trace_data(args, data):
    if args.verbose:
        s = json.dumps(data, indent=2)
        _trace(s)
