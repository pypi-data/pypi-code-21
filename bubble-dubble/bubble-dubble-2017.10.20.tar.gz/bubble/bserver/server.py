#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import asyncio
from .worker import BubbleWorker


class BubbleProtocol(asyncio.Protocol):
    worker = BubbleWorker()

    def connection_made(self, transport):
        self.transport = transport
        self.buffer = b''
        peername = transport.get_extra_info('peername')
        print('Connection from {}:{:d}'.format(*peername))
        self.worker.resetSent()

    def data_received(self, data):
        self.buffer += data
        buf = self.buffer.split(b'\r\n')
        self.buffer = buf[-1]
        for request in buf[:-1]:
            try:
                decoded_request = json.loads(request.decode())
            except json.JSONDecodeError:
                return
            response = self.worker.parse(decoded_request)
            self.transport.write(response)
