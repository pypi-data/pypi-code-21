#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, unicode_literals

from joker.broker import get_resource_broker
from sqlalchemy.ext.declarative import declarative_base


rb = get_resource_broker()


# Base = declarative_base(bind=rb.primary.engine)
Base = declarative_base()

