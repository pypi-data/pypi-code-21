# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""Module defines a single method get_logger that returns logger with set logging level."""

import logging

LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}


def get_logger(p_name, p_level='info'):
    """
    Return logger with p_name as name. And logging level p_level.

    p_level should be in (starting with the most talkactive): 'debug', 'info', 'warning', 'error', 'critical'.
    """
    logger = logging.getLogger(p_name)
    if len(logger.handlers) == 0:
        # Some module migh be imported few times. In every get_logger call
        # with p_name = "X" we return the same instance of logger, bu we must
        # ensure, that the logger has no more than one handler.
        handler = logging.StreamHandler()

        level = LEVELS[p_level]
        logger.setLevel(level)
        handler.setLevel(level)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
