'''
A set of messages for failure handling.

Created on Nov 13, 2017

@author: aevans
'''

from reactive.message.base_message import Message


class SetRestartStrategy(Message):
    """
    Sets the Restart Strategy based on the corresponding enum in the failure
    package.
    """
    pass
