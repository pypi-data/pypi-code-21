"""
This module contains subscriber role to AWS services
"""


class Subscriber(object):
    """
    Subscribe messages from SQS
    """
    @staticmethod
    def subscribe_to_queue(transport, delete_messages=True):
        """
        Subscribe to a queue
        """
        return transport.receive_messages(delete_messages)

    @staticmethod
    def subscribe_to_cache(transport):
        """
        Subscribe to AWS caching service
        """
        return transport.receive_messages()
