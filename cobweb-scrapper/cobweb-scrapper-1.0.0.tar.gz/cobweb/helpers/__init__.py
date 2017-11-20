import functools
import multiprocessing
import threading
from collections import deque

import requests


def is_connected_to_internet():
    try:
        requests.get('http://216.58.192.142', timeout=2)
        return True
    except requests.exceptions.ConnectionError:
        return False


class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Rectifier(threading.Thread, metaclass=Singleton):

    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = deque()
        self.process_lock = multiprocessing.Lock()

    def run(self):
        if not self.queue:
            raise ValueError("No queue to take tasks from")
        while True:
            try:
                task = self.queue.pop()
            except IndexError:
                pass
            else:
                self.process_lock.acquire()
                task[0](*task[1], **task[2])
                self.process_lock.release()


def sequential(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        rectifier = Rectifier()
        rectifier.queue.appendleft((func, args, kwargs))
        if not rectifier.is_alive():
            rectifier.start()

    return inner
