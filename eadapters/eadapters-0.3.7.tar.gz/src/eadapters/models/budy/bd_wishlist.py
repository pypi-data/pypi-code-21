#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import bd_common

from .. import wishlist

class BDWishlist(wishlist.EWishlist, bd_common.BDCommon):
    pass
