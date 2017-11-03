# encoding: utf-8

u"""
============================================================
Changes the uri by replacing the value
in 'filter' with the value in 'parameters'.
------------------------------------------------------------
Filter: string to match in uri e.g. .com
Parameters: new value e.g. .co.uk
------------------------------------------------------------
"""

import logging_helper

logging = logging_helper.setup_logging()


def modify(uri,
           parameters):

    string_to_match = parameters.filter
    replacement_value = (parameters.override
                         if parameters.override
                         else parameters.params)

    uri = uri.replace(string_to_match,
                      replacement_value)

    return uri
