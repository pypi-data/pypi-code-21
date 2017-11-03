# encoding: utf-8

u"""
============================================================
Delays the response for a number of seconds.
------------------------------------------------------------
Filter     : A string to match in the request.
             Leave blank to modify for all requests.
Override   : N/A
Parameters : wait value in seconds
============================================================
"""

import time
import logging_helper

logging = logging_helper.setup_logging()


def modify(request,
           response,
           parameters):

    if parameters.passes_filter(value=request,
                                wildcards=u''):
        # Setup parameters
        wait = (float(parameters.params)
                if parameters.params
                else 0)  # Set a default timeout

        logging.info(u'Generating timeout for {wait} seconds'
                     .format(wait=wait))

        # Wait
        time.sleep(wait)

        logging.debug(u'Timeout elapsed, continuing...')

    return response
