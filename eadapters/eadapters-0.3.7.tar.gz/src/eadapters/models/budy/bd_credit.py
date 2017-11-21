#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import bd_common

from .. import credit

class BDCredit(credit.ECredit, bd_common.BDCommon):
    pass
