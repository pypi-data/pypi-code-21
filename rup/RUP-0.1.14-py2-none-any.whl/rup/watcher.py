import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from util import determine_run_number, is_data, is_rup, is_run_log, is_log
import logging
import threading
import os


class WatchedFile:

    def __init__(self, path, n):
        self.path = path
        self.n = n
        self.mod_time = None
        self.print_time = -1
        self.reset_mod_time()
        self.is_data = is_data(path)
        self.is_rup = not self.is_data

    def reset_mod_time(self):
        self.mod_time = time.time()

    def reset_print_time(self):
        self.print_time = time.time()


def infer_file(path):
    if is_data(path) or is_rup(path) or is_log(path):
        n = determine_run_number(path)
    elif is_run_log(path):
        n = -1
    else:
        return None

    return WatchedFile(path, n)


class Provider:

    def __init__(self):
        self._observers = []
        self.logging = logging.getLogger(self.__class__.__name__)

    def add_observer(self, obs):
        self._observers.append(obs)

    def notify_observes(self, f):
        for obs in self._observers:
            try:
                obs(f)
            except Exception as e:
                self.logging.error("Notifying observer failed:")
                self.logging.error(e)

    def stop(self):
        pass


class DirectoryIterator(Provider):

    def __init__(self, directory):
        Provider.__init__(self)
        self.directory = os.path.realpath(directory)
        self.logging = logging.getLogger(self.__class__.__name__)
        self.logging.info("Iterating {}".format(self.directory))

    def run(self):

        for subdir, dirs, files in os.walk(self.directory):
            for f in files:
                file_path = os.path.join(subdir, f)
                wf = infer_file(file_path)
                if wf is not None:
                    self.notify_observes(wf)


class Watcher(Provider):

    def __init__(self, directory, timeout):
        Provider.__init__(self)
        self.observer = Observer()
        self.directory = os.path.realpath(directory)
        self.event_handler = None
        self.timeout = timeout
        self.logging = logging.getLogger(self.__class__.__name__)
        self.logging.info("Watching {} with timeout {}".format(self.directory, self.timeout))

    def run(self):
        self.event_handler = WatcherEventHandler()
        self.observer.schedule(self.event_handler, self.directory, recursive=True)
        self.observer.start()

        t = threading.Thread(target=self.__watch)
        t.daemon = True
        t.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

    def __watch(self):
        handler = self.event_handler

        trash = []

        while True:
            try:
                for key, f in handler.watching.iteritems():
                    diff = int(time.time() - f.mod_time)
                    self.logging.debug("{} is {} seconds old".format(f.path, diff))
                    if diff > self.timeout:
                        trash.append(key)
                        self.logging.info("{} is {} seconds old. Retiring.".format(f.path, diff))
                        self.notify_observes(f)

                for key in trash:
                    handler.watching.pop(key)

                trash = []

                time.sleep(5)
            except Exception as e:
                self.logging.error(e.message)


class WatcherEventHandler(FileSystemEventHandler):

    def __init__(self):
        self.watching = {}
        self.logging = logging.getLogger(self.__class__.__name__)

    def on_any_event(self, event):
        event_type = event.event_type
        if event.is_directory or event_type == 'deleted':
            return None

        if event_type == 'moved':
            path = event.dest_path
        else:
            path = event.src_path

        wf = infer_file(path)
        if wf is None:
            self.logging.debug("{} is not recognized".format(path))
            return

        run = self.watching.get(path, wf)
        if event_type == "created":
            self.logging.info("{} {}".format(path, event_type))
        if time.time() - run.print_time > 1:
            self.logging.debug("{} {}".format(path, event_type))
            run.reset_print_time()

        run.reset_mod_time()
        self.watching[path] = run

