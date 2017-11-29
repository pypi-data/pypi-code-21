# -*- coding: utf-8 -*-
"""
The command line interface kit.

Clik is a tool for writing complex command-line interfaces with minimal
boilerplate and bookkeeping.

This top-level package pulls together the end user API from the various
modules within clik.

:author: Joe Joyce <joe@decafjoe.com>
:copyright: Copyright (c) Joe Joyce and contributors, 2009-2017.
:license: BSD
"""
#: Current version.
#:
#: :type: :class:`str`
__version__ = '0.92.1'


# LINT: Ignore unused import violations. This module isn't meant to "do"
#       anything, just to make clik's API available to the end user.
from clik.app import app, args, current_app, g, parser  # noqa: F401
from clik.app import run_children, unknown_args  # noqa: F401
from clik.command import catch  # noqa: F401
