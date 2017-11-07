import logging, time
from pycommonlib.ali.mns.queue import Queue
from pycommonlib.ali.mns import Message


class MessageQueue(object):
    def __init__(self, name, endpoint):
        self.name = name
        self.endpoint = endpoint
        self.queue = Queue(name, endpoint)
        self.logger = logging.getLogger('MessageQueue_{}'.format(name))
        self.subscripiton = []

    def push(self, data):
        self.queue.send_message(Message(data))

    def pop(self):
        receivedMessage = self.queue.receive_message(10)
        return receivedMessage

    def subscribe(self, fun):
        self.subscripiton.append(fun)

    def loop(self, maxExeTimes=5, sleep=10, exist_when_error=True):
        exeTimes = 0
        while True:
            exeTimes = exeTimes + 1
            recv_msg = None
            try:
                recv_msg = self.pop()
                if recv_msg:
                    self.logger.debug('message received. {}'.format(recv_msg))
                    for f in self.subscripiton:
                        try:
                            f(recv_msg.Data)
                        except:
                            self.logger.exception('{} failed'.format(f.__name__))
                            raise
                        else:
                            self.logger.debug('{} succeed'.format(f.__name__))
                else:
                    time.sleep(sleep)
            except:
                self.logger.exception('process message failed')
                if exist_when_error:
                    break
                else:
                    time.sleep(sleep)
            else:
                self.logger.debug('process message successfully')
                if recv_msg:
                    self.queue.delete_message(recv_msg.ReceiptHandler)
            if exeTimes >= maxExeTimes:
                break
