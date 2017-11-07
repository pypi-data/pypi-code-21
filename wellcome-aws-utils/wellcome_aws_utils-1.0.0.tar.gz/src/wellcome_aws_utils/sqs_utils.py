# -*- encoding: utf-8 -*-

import boto3
import daiquiri


logger = daiquiri.getLogger(__name__)


def get_messages(queue_url, delete=False, batch_size=10):
    """
    Gets messages from an SQS queue.  If ``delete`` is True, the
    messages are also deleted after they've been read.
    """
    client = boto3.client('sqs')
    while True:
        # We batch message responses to reduce load on the SQS API.
        # Note: 10 is currently the most messages you can read at once.
        resp = client.receive_message(
            QueueUrl=queue_url,
            AttributeNames=['All'],
            MaxNumberOfMessages=batch_size
        )

        # If there's nothing available, the queue is empty.  Abort!
        try:
            logger.info(
                'Received %d new messages from %s',
                len(resp['Messages']), queue_url)
        except KeyError:
            logger.info('No messages received from %s; aborting', queue_url)
            break

        # If we're deleting the messages ourselves, we don't need to send
        # the ReceiptHandle to the caller (it's only used for deleting).
        # If not, we send the entire response.
        if delete:
            for m in resp['Messages']:
                yield {k: v for k, v in m.items() if k != 'ReceiptHandle'}
        else:
            yield from resp['Messages']

        # Now delete the messages from the queue, so they won't be read
        # on the next GET call.
        if delete:
            logger.info(
                'Deleting %d messages from %s',
                len(resp['Messages']), queue_url)
            client.delete_message_batch(
                QueueUrl=queue_url,
                Entries=[
                    {'Id': m['MessageId'], 'ReceiptHandle': m['ReceiptHandle']}
                    for m in resp['Messages']
                ]
            )
