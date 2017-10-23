import asyncio
import concurrent
import collections
import logging
import datetime as dt
import uuid
import json

import zmq
import zmq.asyncio


class Message:
    def __init__(self, client_id, message):
        self.date_added = dt.datetime.utcnow()
        self.client_id = client_id
        self.message = message


class SchedulerCode:
    WORKER = b"MDPW01"
    CLIENT = b"MDPC01"
    READY = bytes([1])
    REQUEST = bytes([2])
    REPLY = bytes([3])
    HEARTBEAT = bytes([4])
    DISCONNECT = bytes([5])


class Scheduler:
    DEFAULT_PROTOCOL = "tcp"
    DEFAULT_PORT = 8000
    DEFAULT_HOSTNAME = '0.0.0.0'
    DEFAULT_MAX_MESSAGES_PER_WORKER = 1_000

    def __init__(self, stop_event, protocol=DEFAULT_PROTOCOL, port=DEFAULT_PORT, hostname=DEFAULT_HOSTNAME, loop=None):
        self.stop_event = stop_event
        self.loop = loop or asyncio.get_event_loop()
        self.logger = logging.getLogger('mdp.scheduler')
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.logger.info(f'Binding ZMQ socket client to {protocol}://{hostname}:{port}')
        self.socket.bind(f'{protocol}://{hostname}:{port}')
        self.messages = {}
        self.workers = {}
        self.services = collections.defaultdict(lambda: {'workers': set(), 'queue': asyncio.Queue(), 'task': None, 'next_worker': asyncio.PriorityQueue()})

    async def _handle_client_message(self, client_id, multipart_message):
        service, *message_data = multipart_message
        self.logger.debug(f'adding client {client_id} message for service {service} to queue')
        message_uuid = uuid.uuid4().bytes
        message = Message(client_id, message_data)
        self.messages[message_uuid] = message
        await self.services[service]['queue'].put(message_uuid)

    async def _handle_service_queue(self, service):
        try:
            while True:
                message_uuid = await service['queue'].get()
                message = self.messages[message_uuid]
                priority, worker_id = await service['next_worker'].get()
                worker = self.workers[worker_id]
                worker['messages'].add(message_uuid)
                await self.socket.send_multipart([
                    worker_id, b'', SchedulerCode.WORKER, SchedulerCode.REQUEST,
                    message_uuid, b'', *message.message
                ])
                if len(worker['messages']) < worker['config']['max_messages']: # schedule another task?
                    await service['next_worker'].put((len(worker['messages']), worker_id))
                service['queue'].task_done()
                service['next_worker'].task_done()
        except asyncio.CancelledError:
            self.logger.info('stopping worker for service')

    def parse_worker_config(self, bytes_config):
        try:
            config = json.loads(bytes_config.decode('utf-8'))
        except json.decoder.JSONDecodeError:
            config = {}
        if 'max_messages' not in config:
            config['max_messages'] = self.DEFAULT_MAX_MESSAGES_PER_WORKER
        return config

    async def _handle_worker_message(self, worker_id, multipart_message):
        message_type = multipart_message[0]
        if message_type == SchedulerCode.READY:
            service_name = multipart_message[1]
            service = self.services[service_name]
            self.logger.info(f'adding worker {worker_id} for service {service_name}')
            self.workers[worker_id] = {'service': service_name, 'config': self.parse_worker_config(multipart_message[2]), 'messages': set()}
            service['workers'].add(worker_id)
            await service['next_worker'].put((0, worker_id))
            if len(service['workers']) == 1:
                service['task'] = asyncio.ensure_future(self._handle_service_queue(service))
        elif message_type == SchedulerCode.REPLY:
            message_uuid = multipart_message[1]
            worker = self.workers[worker_id]
            worker['messages'].remove(message_uuid)
            message = self.messages.pop(message_uuid)
            self.logger.debug(f'sending client {message.client_id} message response from worker {worker_id}')
            await self.socket.send_multipart([
                message.client_id, b'', SchedulerCode.CLIENT,
                self.workers[worker_id]['service'], *multipart_message[3:]
            ])
            if len(worker['messages']) == (worker['config']['max_messages'] - 1):
                service = self.services[worker['service']]
                await service['next_worker'].put((len(worker['messages']), worker_id))
        elif message_type == SchedulerCode.HEARTBEAT:
            self.logger.debug('responding with heartbeat')
            await self.socket.send_multipart([
                worker_id, b'', SchedulerCode.WORKER, SchedulerCode.HEARTBEAT
            ])
        elif message_type == SchedulerCode.DISCONNECT:
            if worker_id in self.workers:
                worker = self.workers[worker_id]
                service = self.services[worker['service']]
                if len(service['workers']) == 1: # last worker
                    self.logger.info(f'canceling {worker["service"]} service queue task')
                    service['task'].cancel()
                    try:
                        await service['task']
                    except concurrent.futures.CancelledError:
                        pass
                    service['task'] = None
                self.logger.info(f'removing worker {worker_id} for service {worker["service"]} - rescheduling {len(worker["messages"])} messages')
                service['workers'].remove(worker_id)
                for _ in range(service['next_worker'].qsize()): # Remove worker from next_worker queue
                    value = service['next_worker'].get_nowait()
                    if value[1] != worker_id:
                        service['next_worker'].put_nowait(value)
                for message in worker['messages']: # Requeue messages from worker
                    await service['queue'].put(message)
                self.workers.pop(worker_id)

    async def on_recv_message(self):
        while not self.stop_event.is_set():
            multipart_message = await self.socket.recv_multipart()
            client_id, _1, message_sender, *message = multipart_message
            if message_sender == SchedulerCode.WORKER:
                await self._handle_worker_message(client_id, message)
            elif message_sender == SchedulerCode.CLIENT:
                await self._handle_client_message(client_id, message)
            else:
                raise ValueError()

    def run(self):
        self.loop.run_until_complete(self.on_recv_message())

    def disconnect(self):
        self.stop_event.set()
        self.socket.close()
