import logging

from . import SQSResource
from ..serializers import JSON


class Source(SQSResource, JSON):
    """Uses the boto3 Queue object.

    Uses get_queue_by_name(), or receives the queue during initialization step.

    Relies on receive_messages() as described in:
    http://boto3.readthedocs.org/en/latest/reference/services/sqs.html#queue
    """

    # http://boto3.readthedocs.org/en/latest/reference/services/sqs.html
    # http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-long-polling.html
    # https://github.com/boto/boto3-sample/blob/master/transcoder.py

    #
    # TODO: use queue name for logging.
    #

    # For reference value, see:
    # http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-long-polling.html
    LONG_POLLING_TIMEOUT = 20  # seconds
    MAX_NUMBER_OF_MESSAGES = 10

    def __init__(self, queue=None, queue_name=None, region_name=None, use_compression=True):
        """Prepare the source with a configured SQS backend.

        The SQS queue object can be passed, or the queue name. If both are
        passed, the object is preferred.

        Keyword parameters:
        * queue: SQS client object.
        * queue_name: alternatively, the queue name.
        * region_name: optionally, the region name the SQS queue lives in.
        * use_compression: decompress message using zlib after receiving (True by default)
        """
        self.use_compression = use_compression
        self.log = logging.getLogger('sqs.source')
        if queue is None:
            queue = self._get_queue(queue_name, region_name)
        self.queue = queue
        self._message_from_queue_generator = self._message_from_queue()
        self.log.debug('using SQS queue URL="%s"' % self.queue.url)

    def _package_from_message(self, msg):
        """Parse the raw package from the message coming from the backend."""
        try:
            if self.use_compression:
                message_body = self.decompress(msg.body)
            else:
                message_body = msg.body
            return self.deserialize(message_body)
        except Exception as e:
            self.log.error('could not parse incoming message:')
            self.log.debug('offending message: %s' % msg.body)
            raise e

    def _message_from_queue(self):
        """Yields a single (deleted) message from backend, or None.

        Uses queue.receive_messages() to poll for a package. Polls the backend
        until it gets a new message. Blocks for LONG_POLLING_TIMEOUT.

        Counts on LONG_POLLING_TIMEOUT seconds being a good polling timeout,
        and 1 being the default number of messages to pull.

        Retrieves MAX_NUMBER_OF_MESSAGES per polling.
        """
        while True:
            # receive_messages() returns a list, even if asked for just one.
            msgs = self.queue.receive_messages(
                WaitTimeSeconds=self.LONG_POLLING_TIMEOUT,
                MaxNumberOfMessages=self.MAX_NUMBER_OF_MESSAGES,
            )
            if msgs:
                for message in msgs:
                    # Delete message from queue, and return it to the caller
                    message.delete()
                    yield message
            else:
                yield None

    def _get_message(self):
        """ Returns a single message, or None."""
        msg = next(self._message_from_queue_generator)
        return msg

    def get_once(self):
        """Returns a package if one is available, or None."""
        msg = self._get_message()
        if msg is not None:
            try:
                msg = self._package_from_message(msg)
            except Exception as e:
                self.log.error('Eror retrieving message: {}'.format(e))
                self.log.warning('dropping offending message')
                msg = None
        return msg

    def get(self, num_tries=-1):
        """Returns a package, or None, after num_tries times.

        Use "num_tries" to specify the number of loops. A value of -1 is an
        infinite loop.
        """
        count = num_tries
        while count != 0:
            pkg = self.get_once()
            if pkg is not None:
                return pkg
            if count > 0:
                count = count - 1
        return None


class Sink(SQSResource, JSON):
    """Uses the boto3 Queue object.

    Uses get_queue_by_name(), or receives the queue during initialization step.

    Relies on send_message() as described in:
    http://boto3.readthedocs.org/en/latest/reference/services/sqs.html#queue
    """

    # http://boto3.readthedocs.org/en/latest/reference/services/sqs.html
    # http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-long-polling.html
    # https://github.com/boto/boto3-sample/blob/master/transcoder.py

    def __init__(self, queue=None, queue_name=None, region_name=None, use_compression=True):
        """Prepare the sink with a configured SQS backend.

        Either the SQS queue object or its name must be passed (queue object is
        preferred).

        Keyword parameters:
        * queue: the queue object.
        * queue_name: alternatively, the queue name.
        * region_name: optionally, the region name the SQS queue lives in.
        * use_compression: compress message using zlib before publishing (True by default)
        """
        self.use_compression = use_compression
        self.log = logging.getLogger('sqs.sink')
        if queue is None:
            queue = self._get_queue(queue_name, region_name)
        self.queue = queue
        self.log.debug('using SQS queue URL="%s"' % self.queue.url)

    def put(self, pkg):
        """Sends the raw package to the queue.

        Positional parameters:
        * the raw package dict.
        """
        msg = self.serialize(pkg)
        self.log.debug('sending to queue JSON encoded package: %s' % msg)
        if self.use_compression:
            msg = self.compress(msg)
        self.queue.send_message(MessageBody=msg)
