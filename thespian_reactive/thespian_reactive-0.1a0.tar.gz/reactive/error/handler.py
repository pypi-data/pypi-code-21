'''
A set of error handlers for better formatting specific errors.

Created on Oct 29, 2017

@author: aevans
'''

import logging
import traceback


def handle_actor_system_fail():
    """
    Handle a failure in the actor system.
    """
    err_msg = traceback.format_exc()
    err_msg = "Error in Actor System\n{}".format(err_msg)
    logging.error(err_msg)


def format_send_receive_error(msg, sender, receiver):
    """
    Create a common format for sender, receiver errors
    """
    return "{}\nSender={}\nReceiver={}".format(msg, sender, receiver)


def format_message_error(msg, expected, actual):
    """
    Format error message when actual and expected receipts differ
    """
    return "{}\nExpected={}\nActual={}".format(msg, str(expected), str(actual))
