import gevent
import gevent.monkey
gevent.monkey.patch_all(thread=False)

import logging
import os
import signal

from django.conf import settings

from .. import watcher

from . import bottle
from .liveserver import LiveServer, LIVE_PORT
from .utils import IP_ANY, CleanChildProcesses, pid_exists, with_lock
from .wsgi_worker import Worker

logger = logging.getLogger(__name__)


class Supervisor:
    PID_NAME = 'livereload.pid'
    RELOAD_SIGNAL = signal.SIGUSR1
    RESTART_SIGNAL = signal.SIGHUP

    WORKER_DEAD = 0
    WORKER_STARTING = 1
    WORKER_READY = 2
    WORKER_CLOSING = 3

    @classmethod
    def pid_path(cls):
        # FIXME: Eventually figure out how to get the path of the main app.py
        #        so that the pid file is created there.
        return cls.PID_NAME

    @classmethod
    def save_pid(cls):
        pid = str(os.getpid())
        pid_path = cls.pid_path()
        with open(pid_path, 'w', encoding='utf-8') as pid_file:
            logger.info("Writing supervisor PID " + pid + " to " + pid_path)
            pid_file.write(pid)

    @classmethod
    def kill(cls, sig_num):
        pid_path = cls.pid_path()
        if os.path.exists(pid_path):
            with open(pid_path, 'r', encoding='utf-8') as pid_file:
                try:
                    server_pid = int(pid_file.read())
                    os.kill(server_pid, sig_num)
                    return True
                except:
                    pass
        return False

    def __init__(self, django_ip=IP_ANY, django_port=8080, live_port=LIVE_PORT, live_ip=None):
        logger.info("Initializing Supervisor")
        self._live_server = LiveServer(ip=live_ip or django_ip, port=live_port)
        self.dj_ip = django_ip
        self.dj_port = django_port
        self._worker_pid = None
        self._worker_status = self.WORKER_DEAD
        self._worker_lock = gevent.lock.BoundedSemaphore(1)

        # Kill any previously running supervisor
        killed_old = self.kill(signal.SIGKILL)
        if killed_old:
            logger.info("Killed previously running supervisor")
        self.save_pid()

        # Install signal handlers
        signal.signal(self.RELOAD_SIGNAL, self.signal_handler) # Reload client
        signal.signal(self.RESTART_SIGNAL, self.signal_handler)  # Restart child server
        signal.signal(Worker.READY_SIGNAL, self.signal_handler) # Child server ready

    def signal_handler(self, sig_num, stack_frame):
        if sig_num == self.RELOAD_SIGNAL:
            logger.info("Received signal {sig} forcing client reload.".format(sig=sig_num))
            self._live_server.reload()
        elif sig_num == self.RESTART_SIGNAL:
            logger.info("Received signal {sig} restarting server.".format(sig=sig_num))
            self.restart_worker()
        elif sig_num == Worker.READY_SIGNAL:
            logger.info("Received signal {sig} worker ready.".format(sig=sig_num))
            self._worker_status = self.WORKER_READY
            self._live_server.status('ready')
            self._live_server.reload()

    def _path2url(self, path):
        return settings.STATIC_URL+'/'+path

    def _watcher(self):
        logger.info("Staring watcher")
        w = watcher.Watcher()
        for path, file_type in w.changes():
            if path is not None:
                if file_type == watcher.Watcher.STATIC:
                    logger.info("Reloading client because '{path}' changed".format(path=path))
                    self._live_server.reload(self._path2url(path))
                else:
                    logger.info("Restarting server because '{path}' changed".format(path=path))
                    self.restart_worker()

    def _spawn_worker(self):
        with self._worker_lock:
            self._live_server.status('starting')
            self.kill_worker(Worker.RESTART_SIGNAL)

            # If the previous worker didn't exit by now, kill it forcefully
            self.kill_worker(signal.SIGKILL)

            self._worker_pid = Worker.spawn(ip=self.dj_ip, port=self.dj_port, live_url=self._live_server.url)
            self._worker_status = self.WORKER_STARTING

    def restart_worker(self):
        if self._worker_lock.locked():
            return False
        self._spawn_worker()


    def kill_worker(self, signum):
        if pid_exists(self._worker_pid):
            try:
                logger.info("Sending signal {sig} to worker PID {pid}".format(pid=self._worker_pid, sig=signum))
                os.kill(self._worker_pid, signum)
            except:
                pass

    def _watch_children(self):
        while True:
            pid, exit_status = os.waitpid(-1, options=0)
            exit_code = os.WEXITSTATUS(exit_status)
            if not self._worker_lock.locked() and pid == self._worker_pid:
                if exit_code != Worker.RESTART_EXIT_CODE:
                    logger.info("Worker died with unexpected exit code "+str(exit_code))
                    logger.info("Waiting for source change/signal to restart")
                self._live_server.status('dead')
                self._worker_status = self.WORKER_DEAD

    def run_forever(self):
        gevent.spawn(self._watcher)
        gevent.spawn(self._live_server.serve_forever)

        with CleanChildProcesses():
            self._spawn_worker()
            self._watch_children()



