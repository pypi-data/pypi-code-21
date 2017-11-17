# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, absolute_import)
#
# This script is duplicated as sim.py (for hydraulic and WQ simulation)
# and th.py (for thermo-hydraulic simulation)
#
import os.path as OP
import sys

from ganessa._getdll import _getdllinfo

# required numpy version
_req_np_vers = (1, 7, 0)
try:
    from numpy import __version__ as np_vers
    npv = tuple(map(int, np_vers.split('.')))
    if npv < _req_np_vers:
        raise ImportError
    del npv, np_vers
except ImportError:
    from util import unistr
    uname = unistr(__name__)
    print('Error importing "' + uname + '": numpy '+ 
          '.'.join(map(str, _req_np_vers)) +' or above is required.')
    sys.exit('Required component for ' + uname + ' not found.')


# call from ganessa.sim --> Piccolo; ganessa.th --> Picalor
_bth = __name__.endswith('th')

# lookup for a matching folder, dll and import it
_dll_dir, _dll_name, _dll_api = _getdllinfo(_bth)
if not _dll_api:
    raise ImportError('DLL ' + _dll_name + ': not found or too old.\n')

try:
    _lang = _dll_dir.split('_')[-1]
except IndexError:
    _lang = 'FR'
    
# Binary result file
subdir = dict(FR= 'Travail', UK='Work', ESP= 'Trabajo', ENG='Work')
_workdir = OP.join(_dll_dir, subdir.get(_lang.upper(), ''))
del subdir
if OP.exists(_workdir):
    _fresult = OP.join(_workdir, 'result.bin')
else:
    _fresult = ''

from ganessa import __version__
# modules for both sim and th
from ganessa.core import *
from ganessa.core import _gencmdw

# modules specific to sim / th
if _bth:
    from ganessa.core_th import *
else:
    from ganessa.core_sim import *
