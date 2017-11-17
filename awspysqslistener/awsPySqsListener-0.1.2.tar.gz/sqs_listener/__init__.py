import boto3
import boto3.session
import json
import time
import logging
import os
import sys
from sqs_launcher import SqsLauncher
from abc import ABCMeta, abstractmethod

sqs_logger = logging.getLogger('sqs_listener')

class SqsListener(object):
    __metaclass__ = ABCMeta

    def __init__(self, queue, **kwargs):
        self._queue_name = None
        self._poll_interval = kwargs["interval"] if 'interval' in kwargs else 60
        self._queue_visibility_timeout = kwargs['visibility_timeout'] if 'visibility_timeout' in kwargs else '600'
        self._error_queue_name = kwargs['error_queue'] if 'error_queue' in kwargs else None
        self._error_queue_visibility_timeout = kwargs['error_visibility_timeout'] if 'error_visibility_timeout' in kwargs else '600'
        self._queue_url = queue
        self._message_attribute_names = kwargs['message_attribute_names'] if 'message_attribute_names' in kwargs else []
        self._attribute_names = kwargs['attribute_names'] if 'attribute_names' in kwargs else []
        self._force_delete = kwargs['force_delete'] if 'force_delete' in kwargs else False
        self._region_name = kwargs['region_name'] if 'region_name' in kwargs else 'us-east-1'
        # must come last
        self._client = self._initialize_client()


    def _initialize_client(self):
        self._session = boto3.session.Session()
        sqs = self._session.client('sqs', region_name=self._region_name)
        return sqs

    def _start_listening(self):
        # TODO consider incorporating output processing from here: https://github.com/debrouwere/sqs-antenna/blob/master/antenna/__init__.py
        while True:
            messages = self._client.receive_message(
                QueueUrl=self._queue_url,
                MessageAttributeNames=self._message_attribute_names,
                AttributeNames=self._attribute_names,
            )
            if 'Messages' in messages:
                sqs_logger.info( str(len(messages['Messages'])) + " messages received")
                for m in messages['Messages']:
                    receipt_handle = m['ReceiptHandle']
                    m_body = m['Body']
                    message_attribs = None
                    attribs = None

                    # catch problems with malformed JSON, usually a result of someone writing poor JSON directly in the AWS console
                    try:
                        params_dict = json.loads(m_body)
                    except:
                        sqs_logger.warning("Unable to parse message - JSON is not formatted properly")
                        continue
                    if 'MessageAttributes' in m:
                        message_attribs = m['MessageAttributes']
                    if 'Attributes' in m:
                        attribs = m['Attributes']
                    try:
                        if self._force_delete:
                            self._client.delete_message(
                                QueueUrl=self._queue_url,
                                ReceiptHandle=receipt_handle
                            )
                            self.handle_message(params_dict, message_attribs, attribs)
                        else:
                            self.handle_message(params_dict, message_attribs, attribs)
                            self._client.delete_message(
                                QueueUrl=self._queue_url,
                                ReceiptHandle=receipt_handle
                            )
                    except Exception as ex:
                        # need exception logtype to log stack trace
                        sqs_logger.exception(ex)
                        if self._error_queue_name:
                            exc_type, exc_obj, exc_tb = sys.exc_info()

                            sqs_logger.info( "Pushing exception to error queue")
                            error_launcher = SqsLauncher(self._error_queue_name, True)
                            error_launcher.launch_message(
                                {
                                    'exception_type': str(exc_type),
                                    'error_message': str(ex.args)
                                }
                            )

            else:
                time.sleep(self._poll_interval)

    def listen(self):
            sqs_logger.info( "Listening to queue " + self._queue_url)
            if self._error_queue_name:
                sqs_logger.info( "Using error queue " + self._error_queue_url)

            self._start_listening()

    def _prepare_logger(self):
        logger = logging.getLogger('eg_daemon')
        logger.setLevel(logging.INFO)

        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(logging.INFO)

        formatstr = '[%(asctime)s - %(name)s - %(levelname)s]  %(message)s'
        formatter = logging.Formatter(formatstr)

        sh.setFormatter(formatter)
        logger.addHandler(sh)

    @abstractmethod
    def handle_message(self, body, attributes, messages_attributes):
        return
