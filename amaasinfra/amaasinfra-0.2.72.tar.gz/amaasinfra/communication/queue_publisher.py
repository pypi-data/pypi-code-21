"""
This module contains publisher role to AWS services
"""
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueuePublisher(object):
    """
    The current implementation uses SQS as the transport mechanism.
    """

    @staticmethod
    def publish_item(transport, message, message_attributes=None):
        """
        This method is used to publish message by injecting
        transport object like StandardSQS object etc.
        """
        return transport.send_message(message,
                                      message_attributes=message_attributes)

