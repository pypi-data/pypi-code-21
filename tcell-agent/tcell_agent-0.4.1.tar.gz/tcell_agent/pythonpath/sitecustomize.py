# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function

import imp
import os
import sys


tcell_pythonpath = os.path.dirname(__file__)
path = list(sys.path)
if tcell_pythonpath in path:
    del path[path.index(tcell_pythonpath)]


def find_dotted_module(name, path=None):
    '''
    Example: find_dotted_module('mypackage.myfile')

    Background: imp.find_module() does not handle hierarchical module names (names containing dots).

    Important: No code of the module gets executed. The module does not get loaded (on purpose)
    ImportError gets raised if the module can't be found.

    Use case: Test discovery without loading (otherwise coverage does not see the lines which are executed
              at import time)
    '''

    for x in name.split('.'):
        if path is not None:
            path = [path]
        file, path, descr = imp.find_module(x, path)
    return file, path, descr


for p in path:
    try:
        if "newrelic" not in p:
            (file, pathname, description) = find_dotted_module("sitecustomize", p)

            imp.load_module('sitecustomize', file, pathname, description)
            break
    except Exception as e:
        pass


from tcell_agent.instrumentation import run_instrumentations
from tcell_agent.version import VERSION


try:
    started = run_instrumentations()
    if started:
        print("tCell.io Agent: [Info]  Started tCell.io agent v{version} (sitecustomize)".format(version=VERSION))
except Exception as e:
    print(
        "tCell.io Agent: [Error] Could not start tCell.io agent v{version} {e} (sitecustomize)".format(version=VERSION,
                                                                                                       e=e))
    import traceback
    traceback.print_exc()
