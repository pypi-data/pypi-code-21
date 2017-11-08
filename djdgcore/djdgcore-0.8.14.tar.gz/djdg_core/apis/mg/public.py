#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2017/1/17
 """
from __future__ import unicode_literals, absolute_import
import pymongo
from djdg_core.apis.mg import settings


mg = pymongo.MongoClient(
    host=settings.HOST
)
