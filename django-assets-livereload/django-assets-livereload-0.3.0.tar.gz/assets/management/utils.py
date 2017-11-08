import gevent
import gevent.lock
import gevent.monkey
import gevent.queue
gevent.monkey.patch_all(thread=False)

import logging
import os
import signal

logger = logging.getLogger(__name__)

IP_ANY = '0.0.0.0'

class MessageBroker:
    def __init__(self):
        self.q_lock = gevent.lock.BoundedSemaphore(1)
        self.queues = []

    def sub(self):
        queue = gevent.queue.Queue()
        self.q_lock.acquire()
        self.queues.append(queue)
        self.q_lock.release()
        return queue

    def unsub(self, queue, exit_on_empty=None):
        self.q_lock.acquire()
        self.queues.remove(queue)
        self.q_lock.release()
        if exit_on_empty is not None:
            if len(self.queues) == 0:
                exit(exit_on_empty)

    def pub(self, message):
        self.q_lock.acquire()
        queues = [q for q in self.queues]
        self.q_lock.release()
        logger.info("Sending message '"+str(message)+"' to "+str(len(queues))+" client(s).")
        for q in queues:
            q.put(message)

    def __len__(self):
        self.q_lock.acquire()
        ret = len(self.queues)
        self.q_lock.release()
        return ret

class CleanChildProcesses:
    """
        Taken from https://stackoverflow.com/questions/320232/ensuring-subprocesses-are-dead-on-exiting-python-program
    """
    def __enter__(self):
        os.setpgrp() # create new process group, become its leader
    def __exit__(self, type, value, traceback):
        try:
            os.killpg(0, signal.SIGINT) # kill all processes in my group
        except KeyboardInterrupt:
            # SIGINT is delievered to this process as well as the child processes.
            # Ignore it so that the existing exception, if any, is returned. This
            # leaves us with a clean exit code if there was no exception.
            pass

def with_lock(lock, func):
    def wrapped(*args, **kwargs):
        lock.acquire()
        try:
           return func(*args, **kwargs)
        finally:
            lock.release()
    return wrapped

def pid_exists(pid):
    """
        Check For the existence of a unix pid.

        https://stackoverflow.com/questions/568271/how-to-check-if-there-exists-a-process-with-a-given-pid-in-python
    """
    if pid is None:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True
