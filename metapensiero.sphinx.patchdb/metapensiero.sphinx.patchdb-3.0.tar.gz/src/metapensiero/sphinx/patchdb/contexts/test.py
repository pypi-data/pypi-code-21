# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Test context
# :Created:   ven 03 nov 2017 23:55:36 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2017 Lele Gaifax
#

from __future__ import unicode_literals

import sys
from . import ExecutionContext


class TestContext(ExecutionContext):
    language_name = 'test'
