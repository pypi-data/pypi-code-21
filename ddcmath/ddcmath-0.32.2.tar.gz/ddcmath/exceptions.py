#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 by Christian Tremblay, P.Eng <christian.tremblay@servisys.com>
#
# Licensed under GPLv3, see file LICENSE in this source tree.

class InaccuracyException(Exception):
    """
    Context will lead to inaccuracy in computation.
    Result should not be considered correct
    """
    pass