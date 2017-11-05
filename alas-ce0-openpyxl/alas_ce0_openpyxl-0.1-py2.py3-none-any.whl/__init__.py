# coding=utf-8
# Copyright (c) 2010-2017 openpyxl

# @license: http://www.opensource.org/licenses/mit-license.php
# @author: see AUTHORS file


__author__ = "Adonis Cesar Legón Campo"
__author_email__ = "alegon@alasxpress.com"
__license__ = "MIT"
__maintainer_email__ = "alegon@alasxpress.com"
__url__ = "https://pypi.python.org/pypi/alas-ce0-openpyxl"
__version__ = "0.1"

"""Imports for the openpyxl package."""
from openpyxl.compat.numbers import NUMPY, PANDAS
from openpyxl.xml import LXML

from openpyxl.workbook import Workbook
from openpyxl.reader.excel import load_workbook
