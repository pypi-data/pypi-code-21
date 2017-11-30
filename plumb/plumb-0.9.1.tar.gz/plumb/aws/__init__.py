"""
Top level utilities and documentation for the plumb implementation in AWS.
"""
import base64
import json
import zlib

import boto3
import botocore


class CompressionMixin:
    """Mixin to provide compression/decompression capablities."""

    DEFAULT_ENCODING = 'utf-8'

    def compress(self, message):
        return self._b64compress(message)

    def decompress(self, message):
        try:
            # There may be uncompressed messages in the queue
            json.loads(message)
            return message
        except json.decoder.JSONDecodeError:
            return self._b64decompress(message)

    def _b64compress(self, message):
        ''' Returns a base64-encoded string after compression.
            We always return a string, since SNS does not accept bytes. '''
        return base64.b64encode(zlib.compress(bytes(message, self.DEFAULT_ENCODING))).decode(
            self.DEFAULT_ENCODING)

    def _b64decompress(self, message):
        return zlib.decompress(base64.b64decode(message)).decode(self.DEFAULT_ENCODING)


class SQSResource(CompressionMixin):
    """Mixin to provide _get_queue() to fetch a SQS queue by name."""

    def _get_queue(self, queue_name, region_name=None, *, retry_delay=10):
        """Get the queue object by name and region. The function will retry to
        get the requested queue until it is returned.

        A Session for a queue and the SQS resource is always instantiated. The
        Session is never closed.

        looping until the requested queue is returned.

        Positional parameters:
        * the queue name.

        Keyword parameters:
        * retry_delay: the time delay (in seconds) to retry the request, in case it fails. The
        default value is 10.
        * the queue region: the default value is None; behaviour is given by boto3 module.
        Read the following documentation:
        http://boto3.readthedocs.org/en/latest/reference/core/session.html?highlight=session#module-boto3.session
        """
        session = boto3.session.Session(region_name=region_name)
        sqs = session.resource('sqs')
        try:
            queue = sqs.get_queue_by_name(QueueName=queue_name)
        except botocore.exceptions.ClientError:
            raise ValueError('could not connect to SQS queue "{}" in region "{}"'.format(
                queue_name, region_name))
        return queue


class SNSResource(CompressionMixin):
    """Mixin to provide _get_topic() to fetch a SNS topic by name."""

    def _get_topic(self, topic_name, sns=None, region_name=None):
        """Get the topic by name.

        A SNS resource handle can be passed, or one will be obtained with
        default configuration parameters.

        Positional parameters:
        * the topic name.
        * optionally, a SNS handler to get the topic by name.
        """
        if sns is None:
            if region_name is not None:
                session = boto3.session.Session(region_name=region_name)
                sns = session.resource('sns')
            else:
                sns = boto3.resource('sns')
        # Use property of SNS resource: create_topic() is idempotent.
        # http://boto3.readthedocs.org/en/latest/reference/services/sns.html#sns.Client.create_topic
        return sns.create_topic(Name=topic_name)
