###############################################################################
#
# IBT: Isolated Build Tool
# Copyright (C) 2016, Richard Cook. All rights reserved.
#
# Simple wrappers around Docker etc. for fully isolated build environments
#
###############################################################################

from __future__ import print_function

from ibt.util import get_user_info

class Context(object):
    def __init__(self, working_dir):
        self._working_dir = working_dir
        self._user_info = get_user_info(working_dir)

    @property
    def working_dir(self): return self._working_dir

    def user_info(self): return self._user_info
