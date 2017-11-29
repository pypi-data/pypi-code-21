# coding: utf-8

from deployv.messaging.basemsg import BaseWorker
import logging
from deployv.base import errors


_logger = logging.getLogger('deployv')


class RabbitWorker(BaseWorker):
    def __init__(self, configuration_object, sender_class, receiver_class,
                 worker_id):
        super(RabbitWorker, self).__init__(configuration_object, sender_class, receiver_class,
                                           worker_id)

    def run(self):
        """ Worker method, open a channel through a pika connection and
            start consuming
        """
        _logger.info("W%s - waiting for something to do", self._wid)
        try:
            self._receiver.run(self.callback)
        except errors.GracefulExit:
            # Catch the exception raised in the threads when they are being stopped
            pass

    def signal_exit(self):
        """ Exit when finished with current loop """
        self._receiver.stop()
        self.stop_working.set()

    def kill(self):
        """ This kill immediately the process, should not be used """
        self._receiver.stop()
        self.terminate()
        self.join()

    def callback(self, channel, method, properties, body):
        """ This method is executed as soon as a message arrives, according to the
            `pika documentation
            <http://pika.readthedocs.org/en/latest/examples/blocking_consume.html>`_. The
            parameters are fixed according to it, even if the are unused
        """
        channel.basic_ack(delivery_tag=method.delivery_tag)
        message = self.check_message(body)
        if message:
            _logger.info('Received a message worker %s', self._wid)
            self.execute_rpc(message)
