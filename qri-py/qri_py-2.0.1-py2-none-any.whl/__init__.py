# ~*~ coding: utf-8 ~*~

import logging
import multiprocessing
import Queue
import socket
import time

import pyasn1.codec.ber.encoder as ber_encoder

from . import ber as qrischema

log = logging.getLogger('qri')


class MessageSender(multiprocessing.Process):

    def __init__(self, host, port, message_queue):
        super(MessageSender, self).__init__()
        self.daemon = True
        self.host = host
        self.port = port
        self.message_queue = message_queue
        self.running_flag = multiprocessing.Event()
        self.running_flag.set()

    def join(self, timeout=None):
        self.running_flag.clear()
        super(MessageSender, self).join(timeout)

    def run(self):
        log.info('Starting with %s:%s ...', self.host, self.port)
        try:
            self.send_messages()
        except KeyboardInterrupt:
            pass
        log.info('Finished')

    def send_messages(self):

        SOCKET_TIMEOUT = 3  # seconds
        CONNECT_RETRY_DELAY = 2  # seconds
        SEND_RETRY_DELAY = 2  # seconds
        MESSAGE_QUEUE_TIMEOUT = 1  # seconds

        connected = False
        sock = None
        msg_to_send = None
        msg_seq_no = 0

        while self.running_flag.is_set():

            if msg_to_send is None:
                try:
                    msg_to_send = self.message_queue.get(True, MESSAGE_QUEUE_TIMEOUT)
                    msg_seq_no += 1
                except Queue.Empty:
                    continue

            if not connected:
                if sock is not None:
                    sock.close()
                log.info('Connecting to %s:%s ...', self.host, self.port)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(SOCKET_TIMEOUT)
                try:
                    sock.connect((self.host, self.port))
                except socket.error as e:
                    log.error('Failed to connect to %s:%s with error: %s', self.host, self.port, e)
                    log.info('Will retry to connect in %s second(s) ...', CONNECT_RETRY_DELAY)
                    time.sleep(CONNECT_RETRY_DELAY)
                else:
                    log.info('Connected to %s:%s', self.host, self.port)
                    connected = True

            if connected:
                log.debug('Sending message # %d of length %d ...', msg_seq_no, len(msg_to_send))
                try:
                    bytes_consumed = sock.send(msg_to_send)
                except socket.error as e:
                    log.error('Failed to send: %s', e)
                    log.info('Reconnecting ...')
                    connected = False
                    time.sleep(SEND_RETRY_DELAY)
                else:
                    if bytes_consumed != len(msg_to_send):
                        log.error('Failed to send: bytes accepted for sending does not match message length')
                        log.info('Reconnecting ...')
                        connected = False
                        time.sleep(SEND_RETRY_DELAY)
                    else:
                        msg_to_send = None


class Qri(object):

    def __init__(self, host=None, port=None):
        log.info('Setup: %s:%s', host, port)
        self.queue = multiprocessing.Queue()
        self.worker = MessageSender(host, port, self.queue)
        self.worker.start()

    def send(self, peer=None, checksum=None, message=None):
        msg = qrischema.Message()
        msg['peer'] = peer
        msg['checksum'] = checksum
        msg['message'] = message
        msgbytes = ber_encoder.encode(msg)
        self.queue.put(msgbytes)
