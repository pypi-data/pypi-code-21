# encoding: utf8

"""
Created on 2017.10.18

@author: yalei
"""

import logging.handlers
from cotimelog.cologger import ConcurrentTimeRotatingFileHandler

__version__ = '0.2.0'
__author__ = "Yalei Du"
__all__ = [
    "ConcurrentTimeRotatingFileHandler",
]

# Publish this class to the "logging.handlers" module so that it can be use
# from a logging config file via logging.config.fileConfig().
logging.handlers.ConcurrentTimeRotatingFileHandler = ConcurrentTimeRotatingFileHandler
