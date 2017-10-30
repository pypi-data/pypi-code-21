###############################################################################
#
# IBT: Isolated Build Tool
# Copyright (C) 2016, Richard Cook. All rights reserved.
#
# Simple wrappers around Docker etc. for fully isolated build environments
#
###############################################################################

from __future__ import print_function

class Command(object):
    def __init__(self, name, requires_project):
        self._name = name
        self._requires_project = requires_project

    @property
    def name(self): return self._name

    @property
    def requires_project(self): return self._requires_project
