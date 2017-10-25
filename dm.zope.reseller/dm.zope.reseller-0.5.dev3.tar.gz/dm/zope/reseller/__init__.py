# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
"""Zope 2 based reseller application."""
LANGUAGES = ["en", "de", "fr"]

from AccessControl import allow_module

allow_module("Products.statusmessages.interfaces")

# patch the stupid `zope.i18n.config`
from logging import getLogger
logger = getLogger(__name__)
from zope.i18n import config

if config.COMPILE_MO_FILES is False:
  config.COMPILE_MO_FILES = True
  logger.info("allowed compiling mo files")

if config.ALLOWED_LANGUAGES is None:
  from zope import i18n
  config.ALLOWED_LANGUAGES = LANGUAGES
  i18n.ALLOWED_LANGUAGES = LANGUAGES
  logger.info("set allowed languages to %s", LANGUAGES)
