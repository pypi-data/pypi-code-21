# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function

import traceback

from .manager import InstrumentationManager

_test_mode = False


def run_instrumentations():
    from tcell_agent.config import CONFIGURATION
    if CONFIGURATION.enabled:
        # Call the instrumentation functions, only works if they exist
        if InstrumentationManager.initial_instrumentation_run is False:
            InstrumentationManager.initial_instrumentation_run = True
            from tcell_agent.instrumentation import gunicorn_tcell # noqa pylint: disable=unused-variable
            import tcell_agent.instrumentation.djangoinst.app # noqa pylint: disable=unused-variable
            import tcell_agent.instrumentation.flaskinst.app # noqa
            import tcell_agent.instrumentation.hooks.login_fraud # noqa
            import tcell_agent.instrumentation.cmdi  # noqa

    return CONFIGURATION.enabled


def safe_wrap_function(description, func, *args, **kwargs):
    if _test_mode:
        print("[tcell] >" + description + "<")
        return func(*args, **kwargs)
    try:
        return func(*args, **kwargs)
    except Exception as e:
        handle_exception(description, e)


def safe_wrap_function_no_log(description, func, *args, **kwargs):
    if _test_mode:
        print("[tcell] >" + description + "<")
        return func(*args, **kwargs)
    try:
        return func(*args, **kwargs)
    except Exception:
        pass


def handle_exception(msg, e, logger=None):
    if logger:
        logger.error(e)
    else:
        print(msg)
        traceback.print_exc()


class BaseWrapper(object):
    def __init__(self, instance):
        self._instance = instance

    def __getattr__(self, attr):
        if hasattr(self._instance, attr):
            def wrapper(*args, **kw):
                return getattr(self._instance, attr)(*args, **kw)

            return wrapper
        raise AttributeError(attr)
