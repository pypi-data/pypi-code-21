# -*- coding: utf-8 -*-

"""Top-level package for Tessellate."""

__author__ = """Christopher Bevan Barnett"""
__email__ = 'chrisbarnettster@gmail.com'
__version__ = '0.3.4'

# . Set up the logger here
from os import path, remove
import logging
import sys
import logging.config


logging.basicConfig(stream=sys.stdout, level=logging.ERROR,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# from tessellate.utils.pucker import Pucker







# # .. clear old log
# logfile = "tessellate_logging.log"
# if path.isfile(logfile):
#     remove(logfile)

# .. create logger and log to file
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# logger_handler = logging.FileHandler(logfile)
# logger_handler.setLevel(logging.DEBUG)
#
# .. Set Log Formatting
# logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
# logger_handler.setFormatter(logger_formatter)
# logger.addHandler(logger_handler)
# logger.info('Configure Logger Complete')
