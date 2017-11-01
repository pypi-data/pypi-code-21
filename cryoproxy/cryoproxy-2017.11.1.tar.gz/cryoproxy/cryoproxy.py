#!/usr/bin/env python
# -*- coding: utf-8 -*-

import serial
from serial.tools import list_ports
import asyncio


DEFAULT_PORT = 7900
MAX_BUFFER_SIZE = 42 * 10


class PeriodicTask:
    def __init__(self, func, args=None, kwargs=None):
        self.func = func
        self.running = False
        self._stopping = False
        self.interval = 1
        self.args = args or ()
        self.kwargs = kwargs or {}

    def start(self, interval):
        self.interval = interval
        self.running = True
        asyncio.ensure_future(self._run())

    async def _run(self):
        self._stopping = False
        while self.running:
            self.func(*self.args, **self.kwargs)
            await asyncio.sleep(self.interval)
        self._stopping = True

    async def stop(self):
        self.running = False
        while not self._stopping:
            await asyncio.sleep(0.01)


class SerialPort:
    def __init__(self, port):
        self._buffer = b''
        self.sport = serial.Serial(port)
        self.port = port
        self.task = PeriodicTask(self.read)
        self.task.start(0.1)

    def read(self):
        self._buffer += self.sport.read(self.sport.in_waiting)

    def write(self, data):
        self.sport.write(data)

    @property
    def buffer(self):
        b = self._buffer
        self._buffer = b''
        return b

    async def stop(self):
        await self.task.stop()


class Receiver:
    def __init__(self, sock_port, peer_host, peer_port, transport):
        self.buffer = b''
        self.sock_port = sock_port
        self.peer_port = peer_port
        self.peer_host = peer_host
        self.transport = transport


class Worker:
    def __init__(self):
        self.create_sports()
        self.receivers = set()
        self.task = PeriodicTask(self.poll)
        self.task.start(0.1)

    def poll(self):
        for tcp_port in self.sports:
            sport = self.sports[tcp_port]
            buffer = sport.buffer
            for r in self.receivers:
                if r.sock_port == tcp_port:
                    r.transport.write(buffer)

    def create_sports(self):
        self.sports = {}
        tcp_port = DEFAULT_PORT
        for sport in list_ports.comports():
            try:
                self.sports[tcp_port] = SerialPort(sport.device)
            except serial.SerialException as err:
                print(f'Could not connect to serial port {sport}: {str(err)}')
            else:
                print(f'Serial port {sport} on tcp port {tcp_port}')
                tcp_port += 1

    @property
    def tcp_ports(self):
        return self.sports.keys()

    def write_to_serial(self, port, data):
        if port in self.sports:
            self.sports[port].write(data)

    def add_receiver(self, receiver):
        self.receivers.add(receiver)

    def remove_receiver(self, receiver):
        self.receivers.discard(receiver)

    async def stop(self):
        await self.task.stop()
        for sport in self.sports:
            await self.sports[sport].stop()


class SerialProtocol(asyncio.Protocol):
    worker = Worker()

    def connection_made(self, transport):
        self.transport = transport
        self.sock_port = self.transport.get_extra_info('sockname')[1]
        self.peer_host, self.peer_port = transport.get_extra_info('peername')
        self.receiver = Receiver(self.sock_port, self.peer_host, self.peer_port, self.transport)
        self.worker.add_receiver(self.receiver)
        print(f'Connection from {self.peer_host}:{self.peer_port}')

    def data_received(self, data):
        self.worker.write_to_serial(self.sock_port, data)

    def connection_lost(self, exc):
        print(f'Connection lost from {self.peer_host}:{self.peer_port}: {exc}')
        self.worker.remove_receiver(self.receiver)

    @staticmethod
    def tcp_ports():
        return SerialProtocol.worker.tcp_ports

    async def stop(self):
        await self.worker.stop()


def main():
    servers = []
    proto = []
    loop = asyncio.get_event_loop()
    tcp_ports = SerialProtocol.tcp_ports()
    if tcp_ports:
        for port in tcp_ports:
            p = SerialProtocol()
            proto.append(p)
            servers.append(loop.run_until_complete(loop.create_server(lambda: p, '0.0.0.0', port)))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            print('Stopping and cleaning up...')
        finally:
            for p in proto:
                loop.run_until_complete(p.stop())
            for server in servers:
                server.close()
                loop.run_until_complete(server.wait_closed())
            loop.close()
    else:
        print('Serial ports could not be found on this computer. Exiting...')


if __name__ == '__main__':
    main()
