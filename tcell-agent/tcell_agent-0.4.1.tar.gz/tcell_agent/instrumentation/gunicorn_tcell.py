# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import logging

import tcell_agent
from tcell_agent.agent import TCellAgent

_started = False

LOGGER = logging.getLogger('tcell_agent').getChild(__name__)


def instrument_gunicorn():
    from gunicorn.arbiter import Arbiter
    old_func = Arbiter.start

    def start(self):
        if tcell_agent.instrumentation.gunicorn_tcell._started is False:
            LOGGER.info("Staring (gunicorn) agent")
            tcell_agent.instrumentation.gunicorn_tcell._started = True
            TCellAgent.get_agent().ensure_polling_thread_running()
        return old_func(self)

    Arbiter.start = start


try:
    instrument_gunicorn()
except ImportError as ie:
    pass
except Exception as e:
    LOGGER.debug("Could not instrument gunicorn: {e}".format(e=e))
    LOGGER.debug(e, exc_info=True)
