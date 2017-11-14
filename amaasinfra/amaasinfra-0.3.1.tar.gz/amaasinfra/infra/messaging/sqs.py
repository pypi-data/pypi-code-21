import boto3
from datetime import datetime
import json
import uuid


class StandardSQS(object):
    """
    This class is to process the messages by using standard SQS service
    """
    def __init__(self, queue_url):
        self._queue = boto3.resource('sqs').Queue(queue_url)

    def send_message(self, message_body, delay=0, message_attributes=None):
        """
        Sending messages to SQS
        """
        return self._queue.send_message(MessageBody=message_body,
                                        DelaySeconds=delay,
                                        MessageAttributes=message_attributes)

    def receive_messages(self, delete_messages=True, latency_in_seconds=0):
        """
        Retrieving messages could be tricky, since the number of messages to
        be returned is not guaranteed. Sometimes the network latency will
        cause the failure of messages retrieving attempts.

        :return: a generator of messages from SQS
        """
        gen = (message for message in
               self._queue.receive_messages(MessageAttributeNames=['All'],
                                            MaxNumberOfMessages=10,
                                            WaitTimeSeconds=latency_in_seconds))

        for item in gen:
            yield item
            if delete_messages:
                item.delete()


class MonitorMessage(object):
    """
    This should be a utility class acts like a monitor message
    template generator.
    """
    @staticmethod
    def get_default_message(client_id, asset_manager_id, message,
                            item_id=None, item_level=None, item_status=None,
                            item_class=None, item_type=None,
                            item_source=None, version=None, item_date=None, action='Insert'):
        """
        This will generate the default Monitor message template to be sent to
        SQS
        """
        if not client_id or not asset_manager_id:
            return False
        else:
            message = {"client_id": client_id,
                       "action": action,
                       "content": {"asset_manager_id": asset_manager_id,
                                   "item_id": item_id or uuid.uuid4().hex,
                                   "item_level": item_level or 'Error',
                                   "item_status": item_status or 'Open',
                                   "item_class": item_class or 'Exception',
                                   "item_type": item_type or '',
                                   "item_source": item_source or 'TEMP',
                                   "version": version or 1,
                                   "message": message,
                                   "item_date": item_date or str(
                                       datetime.now())}}

            return json.dumps(message)
