# -*- coding: utf-8 -*-
"""Propertyshelf MLS Plone Embedding."""

# python imports
import logging

# zope imports
from plone import api as ploneapi
from zope.i18nmessageid import MessageFactory

# local imports
from ps.plone.mls import config


PLONE_4 = '4' <= ploneapi.env.plone_version() < '5'
PLONE_5 = '5' <= ploneapi.env.plone_version() < '6'

logger = logging.getLogger(config.PROJECT_NAME)
_ = MessageFactory('ps.plone.mls')
