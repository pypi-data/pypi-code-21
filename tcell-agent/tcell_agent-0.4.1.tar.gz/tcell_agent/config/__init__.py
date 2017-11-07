# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
from .configuration import TcellAgentConfiguration

try:
    CONFIGURATION
except NameError:
    CONFIGURATION = TcellAgentConfiguration()
