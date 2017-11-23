# -*- coding: utf-8 -*-


class ResponseError(Exception):
    """
    Generic ResponseError exception.
    """
    def __init__(self, response):
        self.response = response
