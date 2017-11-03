# encoding: utf-8

u"""
============================================================
Replaces the entire uri with the value in 'parameters' if
the value in 'filter' is in the original uri
------------------------------------------------------------
Filter: string to match in uri e.g. www.google.com
Parameters: new value e.g. https://www.google.co.uk/search?q=google
------------------------------------------------------------
"""

import logging_helper

logging = logging_helper.setup_logging()


def modify(uri,
           parameters):
    if parameters.passes_filter(uri):
        uri = parameters.params

    return uri
