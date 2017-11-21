#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import bd_common

from .. import referral

class BDReferral(referral.EReferral, bd_common.BDCommon):

    name = appier.field()

    @classmethod
    def _ident_name(cls):
        return "name"
