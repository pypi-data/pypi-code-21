# -*- coding: utf-8 -*-
from django.template import TemplateSyntaxError

from .utils import ResponseError


class RaiseResponse:
    """
    Processes exceptions, returning a response if it's the case or raising
    the exception.
    """
    def process_exception(self, request, exception):

        if isinstance(exception, ResponseError):
            return exception.response

        if isinstance(exception, TemplateSyntaxError):
            if getattr(exception, 'exc_info', 0):
                try:
                    exception = exception.exc_info[1]
                except:
                    raise exception
