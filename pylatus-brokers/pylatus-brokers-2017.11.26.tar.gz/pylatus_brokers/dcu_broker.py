#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import asyncio
import logging
import argparse
import aioamqp
from . import tools, constants as c

logger = logging.getLogger('DCUbroker')


class DCUBroker:
    def __init__(self, loop, args):
        self.loop = loop
        self.running = False
        self.reconnecting = False
        self.watching = False
        self.transport = None
        self.protocol = None
        self.address = args.address
        self.sleep = args.sleep
        self.path = args.path
        self.stubborn = args.stubborn
        self.cbfs = os.path.join(self.path, '*.cbf')
        self.logs = os.path.join(self.path, '*.log')
        logger.info('DCU broker is running.')

    @property
    def stopped(self):
        return not (self.running or self.watching or self.reconnecting)

    def clean_path(self):
        logger.warning(f'Remove everything under {self.path}')
        for f in glob.iglob(os.path.join(self.path, '*')):
            try:
                os.remove(f)
            except OSError as err:
                logger.error(f'Could not remove {f}: {err}')

    def path_good(self):
        logger.info(f'Checking the directory for watching: {self.path}')
        if not os.path.exists(self.path):
            logger.critical(f'Path {self.path} does not exist. Exiting...')
            return False
        elif not os.path.isdir(self.path):
            logger.critical(f'Path {self.path} is not a directory. Exiting...')
            return False
        else:
            logger.info(f'Path {self.path} is OK, watching it...')
            return True

    async def connect(self):
        logger.info(f'Trying to establish connection to RabbitMQ at {self.address}.')
        host, port = tools.get_hostport(self.address)
        try:
            self.transport, self.protocol = await aioamqp.connect(host, port, on_error=self.reconnect)
            self.channel = await self.protocol.channel()
            await self.channel.queue(c.QUEUE_DCU, durable=True)
        except (aioamqp.AioamqpException, OSError) as err:
            logger.critical(f'Connection to RabbitMQ at {self.address} cannot be established: {err}.')
            self.transport = None
            self.protocol = None
            return False
        else:
            logger.info('Connection to RabbitMQ has been established.')
            return True

    async def setup(self):
        if self.path_good():
            self.clean_path()
        if self.stubborn:
            self.running = True
            asyncio.ensure_future(self.reconnect())
            asyncio.ensure_future(self.watch())
        else:
            if await self.connect():
                self.running = True
                asyncio.ensure_future(self.watch())

    async def watch(self):
        logger.info(f'Sleep time is set to {self.sleep * 1e3} msec.')
        logger.info(f'Configuration seems to be OK. We have started.')
        self.watching = True
        while self.running:
            await asyncio.sleep(self.sleep)
            for file in glob.iglob(self.cbfs):
                await self.check_file(file)
            for file in glob.iglob(self.logs):
                self.remove(file)
        self.watching = False

    async def check_file(self, file):
        chunk = await self.loop.run_in_executor(None, self.read_cbf, file)
        if chunk:
            logger.info(f'Sending to RabbitMQ CBF {file}')
            await self.send(chunk)
            logger.info(f'Done for CBF {file}')

    async def send(self, chunk):
        try:
            await self.channel.basic_publish(
                payload=chunk,
                exchange_name='',
                routing_key=c.QUEUE_DCU,
                properties={
                    'delivery_mode': 2,
                }
            )
        except aioamqp.AioamqpException as err:
            logger.error(f'It seems that the connection to RabbitMQ at {self.address} has been lost: {err}')
            await self.reconnect()
            self.loop.call_later(1, lambda: asyncio.ensure_future(self.send(chunk)))

    async def reconnect(self, exc=None):
        if exc is not None and not isinstance(exc, aioamqp.ChannelClosed):
            logger.error(f'Exception in AMQP: {exc}')
        if not self.reconnecting:
            self.reconnecting = True
            while self.running:
                logger.info(f'Trying to reconnect to RabbitMQ at {self.address} after 1 second...')
                await asyncio.sleep(1)
                if await self.connect():
                    break
            self.reconnecting = False

    def read_cbf(self, filepath):
        logger.info(f'Reading CBF file {filepath}')
        try:
            cbf = open(filepath, 'rb').read()
        except OSError as err:
            logger.error(f'File {filepath} could not be read: {err}. Skipping...')
            return
        else:
            logger.warning(f'Removing file {filepath}')
            self.remove(filepath)
            return cbf

    def remove(self, filepath):
        try:
            os.remove(filepath)
        except OSError as err:
            logger.error(f'Could not remove file {filepath}: {err}')

    async def stop(self):
        self.running = False
        if self.protocol:
            await self.protocol.close()
            self.protocol = None
        if self.transport:
            self.transport.close()
            self.transport = None
        await self.exiting()

    async def exiting(self):
        while not self.stopped:
            await asyncio.sleep(0.1)


def main():
    parser = argparse.ArgumentParser(description='DCU ramdisk watcher.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('path', help='Directory to watch')
    parser.add_argument('-s', '--sleep', dest='sleep', help='Sleep time during watching (sec)',
                        default=c.WATCHDOG_SLEEP, type=float)
    parser.add_argument('-r', '--rabbitmq', dest='address', help='RabbitMQ server address',
                        default=f'{c.RABBITMQ_HOST}:{c.RABBITMQ_PORT}')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='Debug')
    parser.add_argument('-b', '--stubborn', dest='stubborn', action='store_true',
                        help='Do not give up connection at startup if it could not be established')
    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    logging.basicConfig(format='%(asctime)-15s %(message)s')
    logger.setLevel(logging.DEBUG if args.debug else logging.ERROR)
    broker = DCUBroker(loop, args)
    loop.run_until_complete(broker.setup())
    if broker.stopped:
        return
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info('Ctrl-C received. Clean up and exiting...')
    finally:
        loop.run_until_complete(broker.stop())
        loop.close()
