#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import base

class ESubscription(base.EBase):

    email = appier.field()
