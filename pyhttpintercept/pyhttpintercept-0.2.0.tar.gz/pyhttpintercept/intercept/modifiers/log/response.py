# Description: strip out all personalised recommendations in all timeslots
# Author: Hywel Thomas

u"""
================================================================================
Logs the response.  Use before modifying to see the original response or after
modifying to see the response sent to the box
----------------------------------------------------------------------------------
Filter     : N/A
Override   : N/A
Parameters : N/A
==================================================================================
"""

import logging_helper
logging = logging_helper.setup_logging()


def modify(request,
           response,
           parameters):

    content = response.content
    logging.info(u'Response: {r}'.format(r=content))

    return response
