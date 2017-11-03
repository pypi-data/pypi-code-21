# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, absolute_import)
'''
Created on 8 sept. 2017

Functions specific to the thermo-hydraulic (Picalor) simulation

@author: Jarrige_Pi
'''
from ganessa.th import _dll_api
from ganessa.core import (M, DICT, SIMERR, 
            _checkExceptions, _fn_undefined, _ret_errstat)


def solveTH(silent= False, iverb= -1, retry= True):
    '''Runs a thermo-hydraulic steady-state simulation'''
    # SIM IVERB
    if silent: sverb = '-9'
    elif iverb == -1: sverb = '-1'
    else: sverb = str(iverb)
    SIM = M.SIM
    _dll_api.gencmd(SIM.ROOT, SIM.IVER, M.NONE, sverb)
    #  EXEC
    _dll_api.gencmd(-SIM.ROOT, SIM.EXEC, M.NONE)
    istat = _dll_api.commit(0)
    if retry and abs(istat) % SIMERR.SIMERR == SIMERR.ISOL:
        _dll_api.gencmd(-SIM.ROOT, SIM.EXEC, DICT.FULLPER)
        istat = _dll_api.commit(0)
    _checkExceptions(32, istat, 'Error running thermo-hydraulic simulation')
    return istat

try:
    setdensity = _dll_api.setdensity
except AttributeError:
    _fn_undefined.append('setdensity')
    setdensity = _ret_errstat

#****g* ganessa.th/tFunctions
# DESCRIPTION
#   Functions available to ganessa.th ONLY
#****
#****f* tFunctions/symmetric_node
# SYNTAX
#   ids = symmetric_node(sid)
# ARGUMENTS
#   string sid: node ID for which the symmetric (counterpart node on 
#   the other circuit) is looked for
# RESULT
#   * string sid: id of the counterpart node. '' if not found.
# REMARKS
#   * always returns '' with Piccolo/Ganessa_SIM
#   * the counterpart can be found only if the hot and cold circuits are almost symmetric
#   * symmetric_node requires version 2016B (160511) or higher of Picalor/Ganessa TH dll
# HISTORY
#   new in 1.3.6
#****

try:
    _symmetric_node = _dll_api.symmetric_node
except AttributeError:
    _fn_undefined.append('symmetric_node')
    def symmetric_node(sid): return ''
else:
    del _symmetric_node
    def symmetric_node(sid):
        sids, ln = _dll_api.symmetric_node(sid)
        return sids[0:ln]
