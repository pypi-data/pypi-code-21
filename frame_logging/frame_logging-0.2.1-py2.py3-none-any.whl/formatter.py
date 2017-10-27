# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict


class FrameFormatter(object):

    def __init__(self, *args, **kwargs):
        self.format_behaviour = self.get_format_behaviour()
        self.transform_kwargs_methods = self.get_transform_kwargs_methods()
        # default_log_format will look like "{msg}{msisdn}{obj}{correlation_id}"
        # order and content of the format is set in format_behaviour
        self.default_log_format = '{msg}' + ''.join(['{' + key + '}' for key in self.format_behaviour])

    # format methods

    @classmethod
    def get_format_behaviour(cls):
        # must return a dict following this format:
        # key = the kwargs you want to format
        # value = method to format the arg
        raise NotImplementedError('FrameLogging formatter must implement get_format_behaviour')

    # transform methods

    @classmethod
    def get_transform_kwargs_methods(cls):
        # must return a dict following this format:
        # key = extra kwargs passed to log functions
        # value = method to modify kwargs with two parameter: the object and the kwargs dict 
        raise NotImplementedError('FrameLogging formatter must implement get_transform_kwargs_methods')
