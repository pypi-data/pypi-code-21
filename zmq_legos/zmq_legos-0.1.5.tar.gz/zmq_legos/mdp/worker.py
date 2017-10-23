import asyncio
import logging
import datetime as dt
import json

import zmq
import zmq.asyncio

from .scheduler import SchedulerCode


class Worker:
    DEFAULT_PROTOCOL = "tcp"
    DEFAULT_PORT = 8000
    DEFAULT_HOSTNAME = '0.0.0.0'
    DEFAULT_MAX_MESSAGES = 1000

    def __init__(self, stop_event,
                 heartbeat_interval=2, heartbeat_timeout=10,
                 max_messages=DEFAULT_MAX_MESSAGES,
                 protocol=DEFAULT_PROTOCOL, port=DEFAULT_PORT, hostname=DEFAULT_HOSTNAME, loop=None):
        self.stop_event = stop_event
        self.loop = loop or asyncio.get_event_loop()
        self.logger = logging.getLogger('mdp.worker')
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.set_hwm(1000)
        self.uri = f'{protocol}://{hostname}:{port}'
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_timeout
        self.heartbeat_last_response = dt.datetime.utcnow()
        self.max_messages = max_messages
        self.service = None
        self.service_handler = None
        self.queued_messages = asyncio.Queue()
        self.completed_messages = asyncio.Queue()

    async def _handle_send_heartbeat(self):
        while not self.stop_event.is_set():
            if not self.socket.closed and self.heartbeat_last_response < (dt.datetime.utcnow() - dt.timedelta(seconds=self.heartbeat_interval)):
                self.logger.debug('sending heartbeat')
                await self.socket.send_multipart([
                    b'', SchedulerCode.WORKER, SchedulerCode.HEARTBEAT
                ])
            await asyncio.sleep(self.heartbeat_interval)

    async def _handle_check_heartbeat(self):
        while not self.stop_event.is_set():
            previous_heartbeat_check = dt.datetime.utcnow()
            await asyncio.sleep(self.heartbeat_timeout)
            if not self.socket.closed and \
               self.heartbeat_last_response < previous_heartbeat_check:
                self.logger.info(f'no response from broker in {self.heartbeat_timeout} seconds -- reconnecting')
                await self.disconnect()
                await self.connect()

    async def _handle_queued_messages(self):
        while not self.stop_event.is_set():
            client_id, message = await self.queued_messages.get()
            result = await self.service_handler(*message)
            await self.completed_messages.put((client_id, result))
            self.queued_messages.task_done()

    async def _handle_completed_messages(self):
        while not self.stop_event.is_set():
            client_id, result = await self.completed_messages.get()
            await self.socket.send_multipart([
                b'', SchedulerCode.WORKER, SchedulerCode.REPLY, client_id, b'', *result
            ])
            self.completed_messages.task_done()

    async def _on_recv_message(self):
        while not self.stop_event.is_set():
            multipart_message = await self.socket.recv_multipart()
            message_type = multipart_message[2]
            if message_type == SchedulerCode.REQUEST:
                _, _, message_type, client_id, _, *message = multipart_message
                self.logger.debug(f'broker sent request message')
                await self.queued_messages.put((client_id, message))
                self.heartbeat_last_response = dt.datetime.utcnow()
            elif message_type == SchedulerCode.HEARTBEAT:
                self.logger.debug(f'broker response heartbeat')
                self.heartbeat_last_response = dt.datetime.utcnow()
            elif message_type == SchedulerCode.DISCONNECT:
                self.logger.info(f'broker requests disconnect and reconnect')
                await self.disconnect()
                await self.connect()
            else:
                raise ValueError() # unknown event type

    async def run(self, service, service_handler=None):
        """ If no service handler provided it is assumed
        that you handle queue_messages and completed_messages
        """
        self.service = service
        self.service_handler = service_handler
        await self.connect()
        tasks = [
            self._handle_send_heartbeat(),
            self._handle_check_heartbeat(),
            self._handle_completed_messages(),
            self._on_recv_message()
        ]
        if self.service_handler:
            tasks.append(self._handle_queued_messages())
        await asyncio.gather(*tasks)
        await self.disconnect()

    async def connect(self):
        self.logger.info(f'connecting ZMQ socket to {self.uri}')
        self.socket.connect(self.uri)
        worker_config = json.dumps({'max_messages': self.max_messages}).encode('utf-8')
        await self.socket.send_multipart([
            b'', SchedulerCode.WORKER, SchedulerCode.READY, self.service, worker_config
        ])

    async def disconnect(self):
        self.logger.info(f'disconnecting zmq socket from {self.uri}')
        await self.socket.send_multipart([
            b'', SchedulerCode.WORKER, SchedulerCode.DISCONNECT
        ])
        self.socket.disconnect(self.uri)
