# -*- coding: utf-8 -*-
import os
from logentries import LogentriesHandler as _LogentriesHandler


class LogentriesHandler(_LogentriesHandler):
    def __init__(self, token='', **kwargs):
        _token = os.getenv('LOGENTRIES_TOKEN', token)
        super(LogentriesHandler, self).__init__(_token, **kwargs)
