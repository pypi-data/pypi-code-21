#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2017/1/7
 """
from __future__ import unicode_literals, absolute_import
from djdg_core.apis.es import settings
from elasticsearch import Elasticsearch


es = Elasticsearch(settings.HOSTS)
