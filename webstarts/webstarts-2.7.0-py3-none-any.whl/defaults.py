#!/usr/bin/env pythonaaaaa
# -*- coding: utf-8 -*-

"""Applicable to webstarts"""
from inspect import currentframe

__author__ = "john"

LOG_KEY = 'logid'
TRACE_KEY = 'x-cloud-trace-context'
FORMAT = '%(levelname)s %(logid)s %(name)s "%(message)s" %(extras)s'
# FORMAT = '%(levelname)-8s %(logid)-12s %(name)-30s "%(message)-100s" %(extras)s'
FORMAT_DEBUG = '%(levelname)-8s %(logid)-12s %(name)-30s "%(message)-100s"'
CACHE_KEY = lambda *a, **kws: id(currentframe().f_back.f_back.f_locals.get('wrapped'))
