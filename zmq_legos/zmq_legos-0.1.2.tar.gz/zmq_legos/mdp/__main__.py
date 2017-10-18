""" Benchmarks:

# 3000 msg/second for many many workers
3700 msg/second - 10 B
3700 msg/second - 1000 B
3400 msg/second - 10_000 B
# Have gotten 4000 at times
"""

import time
import logging
from multiprocessing import Process, Event
import asyncio

import zmq.asyncio

from .client import Client
from .worker import Worker
from .scheduler import Scheduler

def init_logging():
    logging.basicConfig(level=logging.INFO)


def init_event_loop():
    loop = zmq.asyncio.ZMQEventLoop()
    asyncio.set_event_loop(loop)
    return loop


def init_client(stop_event):
    init_logging()

    async def create_work(loop):
        Client.DEFAULT_PROTOCOL = 'ipc'
        client = Client(loop=loop)
        N = 30_000
        MSG_SIZE = 10
        start_time = time.time()
        for i in range(N):
            await client.submit(b'hello.world', [b'o'*MSG_SIZE])

        for i in range(N):
            service, message = await client.get()
        total_time = time.time() - start_time
        print(f'Total time: {total_time:.3f} [s] for {N} messages size {MSG_SIZE} [{N / total_time} msg/sec]')
        client.disconnect()

    try:
        loop = init_event_loop()
        loop.run_until_complete(create_work(loop))
    except KeyboardInterrupt:
        stop_event.set()


def init_scheduler(stop_event):
    try:
        init_logging()
        Scheduler.DEFAULT_PROTOCOL = 'ipc'
        scheduler = Scheduler(stop_event, loop=init_event_loop())
        scheduler.run()
    except KeyboardInterrupt:
        stop_event.set()


def init_worker(stop_event):
    async def hello_world_worker(*message):
        return (b'1', b'2', b'3')

    try:
        init_logging()
        loop = init_event_loop()
        Worker.DEFAULT_PROTOCOL = 'ipc'
        worker = Worker(stop_event, loop=loop, max_messages=100)
        loop.run_until_complete(worker.run(b'hello.world', hello_world_worker))
    except KeyboardInterrupt:
        stop_event.set()


if __name__ == "__main__":
    NUM_CLIENTS = 1
    NUM_WORKERS = 1

    try:
        stop_event = Event()
        worker_processes = [Process(target=init_worker, args=(stop_event,)) for _ in range(NUM_WORKERS)]
        for worker in worker_processes:
            worker.start()

        scheduler_process = Process(target=init_scheduler, args=(stop_event,))
        scheduler_process.start()

        time.sleep(1)

        client_processes = [Process(target=init_client, args=(stop_event,)) for _ in range(NUM_CLIENTS)]
        for client in client_processes:
            client.start()

        scheduler_process.join()
    except KeyboardInterrupt:
        exit(0)
    finally:
        stop_event.set()
