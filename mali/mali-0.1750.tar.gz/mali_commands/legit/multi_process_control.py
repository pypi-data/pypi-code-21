# coding=utf-8
import logging
import multiprocessing
from threading import Semaphore
from multiprocessing import Pool
import os
import signal


def worker_init(parent_id):
    def sig_int(signal_num, frame):
        os.kill(parent_id, signal.SIGSTOP)

    signal.signal(signal.SIGINT, sig_int)


class MethodWrapper(object):
    def __init__(self, callable_func):
        self.__callable = callable_func

    def __call__(self, *args, **kwargs):
        result = None
        try:
            result = self.__callable(*args, **kwargs)
        except KeyboardInterrupt as e:
            pass

        # It was fine, give a normal answer
        return result


class MultiProcessControl(object):
    def __init__(self, processes=-1):
        processes = multiprocessing.cpu_count() * 2 if processes == -1 else processes
        self.__upload_pool = Pool(processes, worker_init, initargs=(os.getpid(), ))
        self.__max_waiting_semaphore = Semaphore(processes * 4)

    def close(self):
        if self.__upload_pool is None:
            return

        logging.debug('%s closing & joining pool', self.__class__)
        self.__upload_pool.close()
        self.__upload_pool.join()
        logging.debug('%s pool completed', self.__class__)

    def create_callback(self, callback):
        def do_callback(param):
            self.__max_waiting_semaphore.release()
            if callback is not None:
                callback(param)

        return do_callback

    def execute(self, method, args, callback=None):
        self.__max_waiting_semaphore.acquire()
        self.__upload_pool.apply_async(
            MethodWrapper(method),
            args=args,
            callback=self.create_callback(callback))

    def terminate(self):
        self.__upload_pool.terminate()
