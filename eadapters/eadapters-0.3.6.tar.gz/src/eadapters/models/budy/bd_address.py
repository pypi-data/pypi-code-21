#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import bd_common

from .. import address

class BDAddress(address.EAddress, bd_common.BDCommon):

    key = appier.field()

    @bd_common.handle_error
    def create_s(self):
        api = self._get_api()
        self.approve(type = "new")
        address = self.unwrap(default = True)
        address = api.create_address(address)
        address = BDAddress(address)
        return address

    @classmethod
    def _ident_name(cls):
        return "key"
