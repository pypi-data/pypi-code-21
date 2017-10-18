import asyncio
import logging

import zmq
import zmq.asyncio

from .scheduler import SchedulerCode


class Client:
    DEFAULT_PROTOCOL = "tcp"
    DEFAULT_PORT = 8000
    DEFAULT_HOSTNAME = '0.0.0.0'

    def __init__(self, protocol=DEFAULT_PROTOCOL, port=DEFAULT_PORT, hostname=DEFAULT_HOSTNAME, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.logger = logging.getLogger('mdp.client')
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.uri = f'{protocol}://{hostname}:{port}'
        self.logger.info(f'Connecting ZMQ socket to {self.uri}')
        self.socket.connect(self.uri)

    async def submit(self, service, message):
        self.logger.debug(f'sending message to service {service}')
        await self.socket.send_multipart([
            b'', SchedulerCode.CLIENT, service, *message
        ])

    async def get(self):
        multipart_message = await self.socket.recv_multipart()
        service, *message = multipart_message[2], multipart_message[3:]
        self.logger.debug(f'recieving message from service {service}')
        return service, message

    def disconnect(self):
        self.socket.close()
