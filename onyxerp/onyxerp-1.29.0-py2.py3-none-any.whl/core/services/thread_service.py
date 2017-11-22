import threading
from concurrent.futures import ThreadPoolExecutor


class ThreadService(threading.Thread):

    __target = None
    __kwargs = dict()
    __app = object

    def __init__(self, callback, app: object, **keywargs):
        super(ThreadService, self).__init__()
        self.__target = callback
        self.__kwargs = keywargs
        self.__app = app
        self.__kwargs['thread_pooler'] = ThreadPoolExecutor(max_workers=10)

    def run(self):
        self.__target(**self.__kwargs)
        self.__app['log'].info("Background thread finished!")
        return None

    def start(self):
        self.__app['log'].info("Background thread started!")
        return super(ThreadService, self).start()
