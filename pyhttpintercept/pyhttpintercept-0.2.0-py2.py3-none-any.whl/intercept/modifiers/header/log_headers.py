# encoding: utf-8

u"""
============================================================
Logs HTTP headers at Information level.
------------------------------------------------------------
Filter     : string to match in the request url
Override   : N/A
Parameters : header name or part of the header value
             leave blank to log all headers.
============================================================
"""

import logging_helper
import six
from pyhttpintercept.intercept.handlers.support import parse_list_parameters

logging = logging_helper.setup_logging()


def modify(request,
           response,
           parameters):

    if parameters.passes_filter(request):

        # Setup parameters
        parse_list_parameters(parameters)

        params = parameters.params

        log = u''
        for header, value in six.iteritems(headers):
            if not params or header in params or any(p in value for p in params):
                log += (u'\n    Header: "{header}":"{value}"'.format(header=header,
                                                                     value=value))
        logging.info(log)

    return {}
