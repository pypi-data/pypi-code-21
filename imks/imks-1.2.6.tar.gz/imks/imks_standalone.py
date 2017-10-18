# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from collections import OrderedDict as ODict
import re, sys
from unidecode import unidecode
from imks._version import __version__, __date__
from imks import units
from imks import currencies
from . import calendars
from .transformers import command_transformer, unit_transformer, transform

try:
    from objproxies import CallbackProxy, LazyProxy
except:
    from peak.util.proxies import CallbackProxy, LazyProxy

from .config import *

######################################################################
# Completer

def imks_standalone_completer(text, state):
    values = ["Marco", "Laura", "Filippo", "Martina"]
    values = list(filter(lambda x: x.startswith(text), values))
    if state < len(values):
        return values[state]
    else:
        return None

######################################################################
# Code

magic = None

def load_imks(shell=None):
    from imks.magics import imks_magic, change_engine
    global config, magic

    # make sure we have a ~/.imks directory
    import os, os.path
    dotpath = os.path.join(os.environ["HOME"], ".imks")
    if os.path.exists(dotpath):
        if not os.path.isdir(dotpath):
            raise IOError("~/.imks must be a directory")
    else:
        print("Making the directory ~/.imks")
        os.mkdir(dotpath)

    # magic
    imks_magic.imks_doc()
    magic = imks_magic(shell=shell)
        
    # load symbols
    units.load_variables(magic.shell.locals)

    # math engine
    config["engine"] = "math"
    change_engine(magic.shell.locals, config["engine"])

    # input transformers
    config["intrans"] = {}

    # activate true float division
    magic.shell.push(u"from __future__ import division")

    # save current ipython global variables
    config['initial_status'] = magic.shell.locals.keys()

    # copy the local namespace to the global one
    # magic.shell.user_global_ns.update(magic.shell.user_ns)
    
    # run command-line options
    #if "InteractiveShellApp" in ip.config and \
    #  "exec_lines" in ip.config.InteractiveShellApp:
    #    for line in ip.config.InteractiveShellApp.exec_lines:
    #        ip.run_cell(line, store_history=False)
    #    # Remove already executed lines
    #    ip.config.InteractiveShellApp.exec_lines = []
    #    del ip.config.InteractiveShellApp["exec_lines"]
    #    if ip.parent:
    #        ip.parent.exec_lines = []

    # load Startup
    magic.load_imks("Startup")
    
    if config["banner"]:
        print("Welcome to iMKS %s - © Marco Lombardi %s" % (__version__, __date__))
        print("Type %imks -h or ! for help.")

    return magic

