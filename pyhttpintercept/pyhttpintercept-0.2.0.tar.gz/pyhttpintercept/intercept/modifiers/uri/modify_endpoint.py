# encoding: utf-8

u"""
============================================================
Changes the endpoint by replacing the value
in 'filter' with the value in 'parameters'.
------------------------------------------------------------
Filter: original endpoint e.g. www.google.co.uk
Parameters: new endpoint e.g. maps.google.co.uk
------------------------------------------------------------
"""

import logging_helper

logging = logging_helper.setup_logging()

HOSTNAME_INDEX = 2


def modify(uri,
           parameters):

    parts = uri.split(u'/')
    if parameters.passes_filter(parts[HOSTNAME_INDEX]):
        new_endpoint = (parameters.override
                        if parameters.override
                        else parameters.params)
        parts[HOSTNAME_INDEX] = new_endpoint

        uri = u'/'.join(parts)

    return uri
