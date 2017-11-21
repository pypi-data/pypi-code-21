#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import bd_common

from .. import collection

class BDCollection(collection.ECollection, bd_common.BDCommon):
    pass
