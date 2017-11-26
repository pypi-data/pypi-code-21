#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time
import pickle
import random
import asyncio
import logging
import argparse
import aioamqp
import cryio
from . import tools, constants as c, chunks

logger = logging.getLogger('PPUbroker')


class PPUBroker:
    def __init__(self, loop, args):
        self.loop = loop
        self.address = args.address
        self.stubborn = args.stubborn
        self.running = False
        self.reconnecting = False
        self.cleaning = False
        self.transport = None
        self.protocol = None
        # GC timeout between every 1 and 2 hours, then different brokers are not going to do GC at the same time
        self.gc_timeout = random.randint(3600, 7200)
        self.stamps = []
        self.set_zero_header()
        logger.info('PPU broker is running')

    @property
    def stopped(self):
        return not (self.running or self.reconnecting or self.cleaning)

    def set_zero_header(self):
        self.values = {
            'Temperature': [],
            'Flux': [],
            'Lakeshore': [],
            'Blower': []
        }

    async def exiting(self):
        while not self.stopped:
            await asyncio.sleep(0.1)

    async def connect(self):
        logger.info(f'Trying to establish connection to RabbitMQ at {self.address}.')
        host, port = tools.get_hostport(self.address)
        try:
            self.transport, self.protocol = await aioamqp.connect(host, port, on_error=self.reconnect)
            self.channel = await self.protocol.channel()
            await self.set_dcu_queue()
            await self.set_pylatus_exchange()
            await self.set_pylatus_scan_exchange()
        except (aioamqp.AioamqpException, OSError) as err:
            logger.critical(f'Connection to RabbitMQ at {self.address} cannot be established: {err}.')
            self.transport = None
            self.protocol = None
            return False
        else:
            logger.info('Connection to RabbitMQ has been established.')
            return True

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

    async def set_dcu_queue(self):
        logger.info(f'Trying to set the queue {c.QUEUE_DCU} to the DCU.')
        await self.channel.queue(queue_name=c.QUEUE_DCU, durable=True)
        await self.channel.basic_qos(prefetch_count=1, prefetch_size=0, connection_global=False)
        await self.channel.basic_consume(self.handle_chunk, queue_name=c.QUEUE_DCU)
        logger.info(f'The queue {c.QUEUE_DCU} has been set.')

    async def set_pylatus_exchange(self):
        logger.info(f'Trying to set the exchange {c.EXCHANGE_DCU} to Pylatus.')
        await self.channel.exchange(exchange_name=c.EXCHANGE_DCU, type_name='fanout')
        result = await self.channel.queue(queue_name='', exclusive=True)
        queue_name = result['queue']
        await self.channel.queue_bind(exchange_name=c.EXCHANGE_DCU, queue_name=queue_name, routing_key='')
        await self.channel.basic_consume(self.handle_chunk, queue_name=queue_name, no_ack=True)
        logger.info(f'The exchange {c.EXCHANGE_DCU} with the queue {queue_name} has been set.')

    async def set_pylatus_scan_exchange(self):
        logger.info(f'Trying to set the exchange {c.EXCHANGE_SCAN} to Pylatus.')
        await self.channel.exchange(exchange_name=c.EXCHANGE_SCAN, type_name='fanout')
        await self.channel.queue(queue_name=c.EXCHANGE_SCAN, durable=True)
        await self.channel.queue_bind(exchange_name=c.EXCHANGE_SCAN, queue_name=c.EXCHANGE_SCAN, routing_key='')
        logger.info(f'The exchange {c.EXCHANGE_SCAN} with the queue {c.EXCHANGE_SCAN} has been set.')

    async def setup(self):
        if self.stubborn:
            self.running = True
            asyncio.ensure_future(self.gc_stamps())
            asyncio.ensure_future(self.reconnect())
        else:
            if await self.connect():
                self.running = True
                asyncio.ensure_future(self.gc_stamps())

    async def stop(self):
        self.running = False
        if self.protocol:
            await self.protocol.close()
        if self.transport:
            self.transport.close()
        await self.exiting()

    def unpickle(self, body):
        try:
            return pickle.loads(body)
        except pickle.UnpicklingError:
            pass
        try:
            return cryio.cbfimage.CbfHeader(body)
        except cryio.ImageError:
            pass
        logger.error('AMQP chunk is not recognized. Skipping...')

    # noinspection PyUnusedLocal
    async def handle_chunk(self, channel, body, envelope, properties):
        chunk = self.unpickle(body)
        if chunk:
            if isinstance(chunk, chunks.PylatusExperimentParams):
                asyncio.ensure_future(self.experiment_started(chunk))
            elif isinstance(chunk, chunks.PylatusExperimentFinished):
                asyncio.ensure_future(self.experiment_finished(chunk))
            elif isinstance(chunk, chunks.PylatusExperimentValue):
                asyncio.ensure_future(self.add_header_value(chunk))
            elif isinstance(chunk, cryio.cbfimage.CbfHeader):
                asyncio.ensure_future(self.handle_cbf(body, chunk, channel, envelope.delivery_tag))

    async def add_header_value(self, chunk):
        self.values[chunk.key()].append(chunk)

    async def experiment_started(self, p):
        logger.info(f'Pylatus started experiment at {p.timestamp}')
        self.stamps.append([p, None])

    async def experiment_finished(self, p):
        logger.info(f'Pylatus finished experiment at {p.timestamp}')
        for s in self.stamps:
            if s[1] is None:
                s[1] = p

    async def handle_cbf(self, body, header, channel, tag):
        logger.info(f'CBF {header.name}.cbf with timestamp {header.timestamp} has been received')
        estart = await self.get_experiment_params(header)
        if isinstance(estart, chunks.PylatusScanParams):
            await self.handle_scan_cbf(body, header, estart)
        elif isinstance(estart, chunks.PylatusExperimentParams):
            await self.handle_experiment_cbf(header, estart)
        else:
            logger.warning(f'CBF {header.name}.cbf has been discarded.')
        await self.send(lambda: channel.basic_client_ack(delivery_tag=tag))

    async def handle_experiment_cbf(self, header, estart):
        estart.nframes -= 1
        path = os.path.join(estart.path, f'{header.name}.cbf')
        self.patch_header(header, estart)
        try:
            header.save_cbf(path)  # user can delete the dir, then we're dead
        except OSError as err:
            logger.error(f'Could not save CBF {path}: {err}. But we acknowledge it anyway.')
        else:
            logger.info(f'CBF has been saved as {path}')

    async def handle_scan_cbf(self, body, header, estart):
        estart.nframes -= 1
        try:
            cbf = cryio.cbfimage.CbfImage(body)
        except cryio.ImageError as err:
            logger.error(f'Something is wrong with the CBF {header.name}: {err}')
        else:
            cbf.array[cbf.array < 0] = 0
            roi = int(cbf.array.sum())
            chunk = json.dumps((f'{header.name}.cbf', roi))
            logger.debug(f'Scan CBF {header.name} has roi {roi}. Sending to queue...')
            await self.send(lambda: self.channel.basic_publish(
                payload=chunk,
                exchange_name=c.EXCHANGE_SCAN,
                routing_key='',
                properties={
                    'delivery_mode': 2,
                }
            ))
            logger.debug(f'Done for CBF {header.name}')

    async def send(self, func):
        try:
            await func()
        except (aioamqp.AioamqpException, OSError):
            logger.error(f'Sending to RabbitMQ has failed.')
            await self.reconnect()
            self.loop.call_later(1, lambda: asyncio.ensure_future(self.send(func)))

    async def get_experiment_params(self, cbf):
        estart = None
        for i in range(c.WAIT_REPEAT):
            for estart, estop in self.stamps:
                if cbf.timestamp >= estart.timestamp and (estop is None or cbf.timestamp <= estop.timestamp):
                    return estart
            logger.warning(f'CBF {cbf.name}.cbf has older timestamp than the latest expertiment: '
                           f'CBF timestamp vs the latest experiment timestamp: {cbf.timestamp} vs '
                           f'{estart.timestamp if estart else None}')
            logger.info(f'We are waiting for a new possible timestamp during {c.WAIT_TIME + i - 1} seconds, '
                        f'but no longer than {c.WAIT_REPEAT * c.WAIT_TIME} seconds')
            await asyncio.sleep(c.WAIT_TIME)

    def patch_header(self, cbf, estart):
        if estart.oscAxis == 'OMEGA':
            cbf.header['Omega'] = cbf.header['Start_angle']
            cbf.header['Omega_increment'] = estart.step
        elif estart.oscAxis == 'PHI':
            cbf.header['Omega'] = estart.omega
            cbf.header['Omega_increment'] = 0
        for key in self.values:
            if not self.values[key]:
                continue
            first = prev = self.values[key][0]
            for value in self.values[key]:
                if prev.timestamp - c.HTIME_TOLERANCE <= cbf.timestamp <= value.timestamp + c.HTIME_TOLERANCE:
                    cbf.header[key] = value.value
                    break
                prev = value
            else:
                cbf.header[key] = first.value

    async def gc_stamps(self):
        self.cleaning = True
        prev_timestamp = time.time()
        while self.running:
            await asyncio.sleep(0.2)
            timestamp = time.time()
            # if we gc every second, after a few weeks of operation ppu_brokers eat 100% of the CPU
            # doing just garbage collecting most of the time
            # it seems that we care less about memory consumption, but more about performance
            if timestamp - prev_timestamp <= self.gc_timeout:
                continue
            prev_timestamp = timestamp
            for i, (estart, estop) in enumerate(self.stamps[:]):
                if estop is not None and (estart.nframes <= 0 or estart.timestamp - timestamp > c.STAMP_TIMETOLIVE):
                    self.stamps.pop(i)
            if self.stamps:
                for _, estop in self.stamps:
                    if estop:
                        for key in self.values:
                            for i, item in enumerate(self.values[key][::-1]):
                                if item.timestamp < estop.timestamp:
                                    self.values[key] = self.values[key][-i:]
                                    break
                        break
            else:
                self.set_zero_header()
        self.cleaning = False


def main():
    parser = argparse.ArgumentParser(description='PPU Pylatus worker',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-r', '--rabbitmq', dest='address', help='RabbitMQ server address',
                        default=f'{c.RABBITMQ_HOST}:{c.RABBITMQ_PORT}')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='Debug')
    parser.add_argument('-b', '--stubborn', dest='stubborn', action='store_true',
                        help='Do not give up connection at startup if it could not be established')
    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)-15s %(message)s')
    logger.setLevel(logging.DEBUG if args.debug else logging.ERROR)
    loop = asyncio.get_event_loop()
    broker = PPUBroker(loop, args)
    loop.run_until_complete(broker.setup())
    if broker.stopped:
        return
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.warning(f'Ctrl-C received. Cleaning up and exiting...')
    finally:
        loop.run_until_complete(broker.stop())
        loop.close()
