#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import base

class ECurrency(base.EBase):

    name = appier.field()

    currency_code = appier.field()
