#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: exceptions.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 26.09.2017


class ExecutedException(Exception):
    """Exception class for execution
    """
    def __init__(self, error_info):
        self.error_info = error_info

    def __str__(self):
        return self.error_info


class CycleCancelFailedException(Exception):
    """Exception class for cycle cancel failed
    """
    def __init__(self, not_canceled_entrusts):
        self.not_canceled_entrusts = not_canceled_entrusts

    def __str__(self):
        return 'Canceled entrusts incomplete: {0}'.format(
            self.not_canceled_entrusts
        )
