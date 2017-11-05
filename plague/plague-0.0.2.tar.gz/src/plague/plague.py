import asyncio
import collections
import json
import functools
import logging
import random
import socket
import threading
import time

from .infections import Infection

log = logging.getLogger(__name__)


class PeriodicTask:
    def __init__(self, interval, func, loop=None):
        """
        ``PeriodicTask`` is a simple wrapper for scheduling functions
        to be ran on the event loop in intervals

        """
        self.interval = interval
        self.func = func
        self.loop = loop or asyncio.get_event_loop()

    def start(self):
        self._register()

    def _register(self):
        log.debug('Scheduling periodic task: %s', self.func.__name__)
        self.loop.call_later(self.interval, self._run)

    def _run(self):
        log.debug('Executing periodic task: %s', self.func.__name__)
        self.func()
        self._register()


class NaivePlagueClient(object):
    def __init__(self, addr, contaminate=[]):
        """
        Mostly for debugging/testing purposes, this is a really
        hacky way to infect a running plague node

        """
        self.addr = addr
        self.susceptible_nodes = set(contaminate)

    def get_client(self, addr):
        return socket.create_connection(addr)

    def send(self, **kwargs):
        infection = Infection('127.0.0.1', 0, kwargs, self.susceptible_nodes)
        self.get_client().send(bytes(infection))


class Node(object):
    def __init__(self, host, port, contaminate=None, loop=None):
        self.host = host
        self.port = port
        self.loop = loop or asyncio.get_event_loop()
        self.susceptible_nodes = set(contaminate) if contaminate else set()
        self.queued_messages = collections.deque([], 10)
        self.shared = {}

    @property
    def addr(self):
        return (self.host, self.port)

    @property
    def scheduled_tasks(self):
        def heartbeat():
            """ Send an empty infection to ensure cluster members are communicating """
            self.infect()

        def retry_queued_messages():
            try:
                message = self.queued_messages.popleft()
                self.loop.create_task(self._infect(message))
            except IndexError:
                log.debug("No messages queued.")

        return [(5, heartbeat), (30, retry_queued_messages)]

    def _combined_susceptible_nodes(self, other_susceptible, infected):
        # initial set of susceptible nodes is the union of ours and the infections
        combined = self.susceptible_nodes.union(other_susceptible) - infected
        # remove this node from the set so it is not chosen as the selected node
        try:
            combined.remove((self.host, self.port))
        except KeyError:
            # if we are not in the list, we can ignore the exception
            ...

        return combined

    def _queue_message(self, message, node):
        # we don't want to requeue healthchecks, so check for message content
        if message.message:
            log.debug('Queueing message!')
            # only queue for the node that was marked dead
            message.susceptible_nodes = {node}
            self.queued_messages.append(message)

    async def _client_connected_cb(self, reader, writer):
        log.debug('Got connection from %s', writer.get_extra_info('peername'))
        data = await reader.read(1024)
        try:
            # deserialize message
            message = Infection.from_bytes(data)

            log.debug('Acknowledging message.')
            message.infected_nodes.add((self.host, self.port))

            log.debug('Syncing susceptible nodes.')
            self.susceptible_nodes = self.susceptible_nodes.union(message.susceptible_nodes).union(message.infected_nodes)
            message.susceptible_nodes = self.susceptible_nodes

            log.debug('Updating local data with %r', message.message)
            for key, value in message.message.items():
                self.shared[key] = value

            # proliferating infection
            await self.loop.create_task(self._infect(message))
        except Exception:
            log.exception('Unable to parse payload from %s:%s!', message.host, message.port)

    async def _infect(self, message):
        try:
            susceptible_nodes = self._combined_susceptible_nodes(message.susceptible_nodes, message.infected_nodes)
            selected_node = random.choice(list(susceptible_nodes))
        except IndexError:
            log.info("No susceptible nodes available, queueing")
            self.queued_messages.append(message)
            return

        log.debug('-' * 50)
        log.debug('Susceptible nodes => %r', susceptible_nodes)
        log.debug('Node selected is [%r]', selected_node)
        log.debug('-' * 50)

        try:
            _, writer = await asyncio.open_connection(*selected_node, loop=self.loop)
            writer.write(bytes(message))
            await writer.drain()
            writer.close()
        except (ConnectionRefusedError, ConnectionResetError):
            # TODO: should we remove from our susceptible list?
            # ok to keep trying the dead node for now
            log.warning('Selected node %r is dead!', selected_node)
            self._queue_message(message, selected_node)

    def infect(self, **kwargs):
        message = Infection(self.host, self.port, kwargs, self.susceptible_nodes)
        self.loop.create_task(self._infect(message))

    def serve(self):
        """ Returns an asyncio stream server scheduled on the event loop """
        for interval, func in self.scheduled_tasks:
            task = PeriodicTask(interval, func)
            task.start()

        server_coro = asyncio.start_server(
            self._client_connected_cb,
            self.host,
            self.port,
            loop=self.loop,
        )

        return self.loop.run_until_complete(server_coro)


def run_in_loop(server, loop=None):
    loop = loop or asyncio.get_event_loop()
    try:
        loop.run_forever()
    except RuntimeError:
        log.exception('Loop closed prematurely!')
    except KeyboardInterrupt:  # useful when debugging
        pass
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()


class BackgroundNode(threading.Thread):
    def __init__(self, port, contaminate=[], loop=None, *args, **kwargs):
        self.node = Node(
            port,
            contaminate=contaminate,
            loop=loop or asyncio.get_event_loop()
        )
        super().__init__(*args, **kwargs)

    def infect(self, **kwargs):
        message = Infection(
            self.node.host,
            self.node.port,
            kwargs,
            self.node.susceptible_nodes
        )
        f = functools.partial(self.node.loop.create_task, self.node._infect(message))
        self.node.loop.call_soon_threadsafe(f)

    def run(self):
        asyncio.set_event_loop(self.node.loop)
        server = self.node.run()
        run_in_loop(server, self.node.loop)

    def stop(self):
        self.node.loop.call_soon_threadsafe(self.node.loop.stop)
        super().join()
