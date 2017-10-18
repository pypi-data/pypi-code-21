# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Django hook strategy
"""

from logging import getLogger

from ..middlewares import DjangoMiddleware
from .framework import FrameworkStrategy

LOGGER = getLogger(__name__)


def load_middleware_insert(original, middleware):

    def wrapped_load_middleware(self, *args, **kwargs):
        LOGGER.debug("Execute load_middleware_insert")

        # Load original middlewares
        result = original(self, *args, **kwargs)

        # Insert out custom one
        try:
            self._view_middleware.insert(0, middleware.process_view)
            self._response_middleware.append(middleware.process_response)
            self._exception_middleware.append(middleware.process_exception)
        except Exception:
            LOGGER.warning("Error while inserting our middleware", exc_info=True)

        return result

    return wrapped_load_middleware


class DjangoStrategy(FrameworkStrategy):
    """ Strategy for Django peripheric callbacks.

    It injects a custom DjangoFramework that calls callbacks for each
    lifecycle method
    """

    MODULE_NAME = "django.core.handlers.base"
    HOOK_CLASS = "BaseHandler"
    HOOK_METHOD = "load_middleware"

    def __init__(self, strategy_key, observation_queue, queue, import_hook, before_hook_point=None):
        super(DjangoStrategy, self).__init__(strategy_key, observation_queue, queue, import_hook, before_hook_point)

        self.middleware = DjangoMiddleware(self, observation_queue, queue)
        self.wrapper = load_middleware_insert
