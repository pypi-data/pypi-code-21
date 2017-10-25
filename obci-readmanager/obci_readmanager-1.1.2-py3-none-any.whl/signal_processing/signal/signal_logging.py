# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""
Module defines a single method get_logger that returns logger with set logging level.

Change loggin.INFO lines to change logging level.

Author:
    Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
"""
from .. import logging


def get_logger(p_name, p_level='info'):
    """
    Return logger with p_name as name. And logging level p_level.

    p_level should be in (starting with the most talkactive):'debug', 'info', 'warning', 'error', 'critical'.
    """
    return logging.get_logger(p_name, p_level)
