#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import bd_common

from .. import state

class BDState(state.EState, bd_common.BDCommon):
    pass
