# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from ._version import get_versions
__revision__ = get_versions()['full-revisionid']
del get_versions

from .debug import install_debug_handler
install_debug_handler()
del install_debug_handler
