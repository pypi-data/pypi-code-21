import multiprocessing
import functools
import requests


def run_in_another_process(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        p = multiprocessing.Process(target=func, args=args, kwargs=kwargs)
        p.start()
    return inner


@run_in_another_process
def extract_links(queue, link_extractor, response):
    for link in link_extractor.extract(response):
        queue.put(link)


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

