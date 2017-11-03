from datetime import datetime

from amaasinfra.communication.queue_publisher import QueuePublisher


class Publisher(object):
    """
    Publisher class is used to publish monitor messages, cache and
    other logs to the SQS
    """
    @staticmethod
    def publish_to_queue(message, transport, message_attributes=None):
        """
        This static method is used to passing messages to the SQS service
        """
        if not message:
            return False
        if message_attributes is None:
            message_attributes = {'date': {'StringValue': str(datetime.now()),
                                           'DataType': 'String'}}
        return QueuePublisher.publish_item(transport,
                                           message,
                                           message_attributes)

    @staticmethod
    def publish_to_cache():
        pass