#!/usr/bin/env python3

# Automatically maintains files and links in your repository with documentation.
# Syntax:
# docsdir [REPO_PATH [GUARD_TIME]]
#   REPO_PATH - path to the repo, default=./repo
#   GUARD_TIME - time in seconds after the last repository update that the tool waits before regeneration begins, default=1

import os
import sh
import sys
import queue
import signal
import jinja2
import logging
import traceback
import semantic_version as semver
from queue import Queue
from pathlib import Path
from threading import Thread, Event
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, DirModifiedEvent


def process_jinja(dir_path, variables):
    dir_content = [dir_path / p for p in os.listdir(dir_path)]
    jinja_files = [p for p in dir_content if p.suffix == '.jinja']

    logging.debug('Detected jinja files:')
    for f in jinja_files:
        logging.debug(f.name)

    loader = jinja2.FileSystemLoader(str(dir_path))
    envir = jinja2.Environment(loader=loader)

    for f in jinja_files:
        logging.info(f"Processing template '{f.name}'")
        target_path = str(f.with_suffix(''))
        try:
            templ = envir.get_template(f.name)
            templ.stream(**variables).dump(target_path)
        except Exception as ex:
            logging.error(str(ex))
            with open(target_path, 'w') as fh:
                fh.write(f'ERROR in {ex.filename}:{ex.lineno} : {ex}')
                #traceback.print_exc(file=fh)


def process_top_dir(dir_path):
    dir_content = [dir_path / p for p in os.listdir(dir_path)]
    projects = [p.name for p in dir_content if p.is_dir() and not str(p.name).startswith('_')]
    projects = [*sorted(projects)]

    logging.debug('Detected projects:')
    for p in projects:
        logging.debug(p)

    variables = {'projects': projects}
    process_jinja(dir_path, variables)


def process_prj_dir(dir_path):
    dir_content = [dir_path / p for p in os.listdir(dir_path)]
    versions = [p.name for p in dir_content if p.is_dir() and semver.validate(p.name)]
    versions = [*reversed(sorted(versions))]

    logging.debug('Detected versions:')
    for v in versions:
        logging.debug(v)

    link_path = str(dir_path / 'latest')
    if versions:
        latest_version_path = str(dir_path / versions[0])
        sh.ln('-sfnr', latest_version_path, link_path)
    else:
        sh.rm('-f', link_path)

    variables = {'versions': versions}
    process_jinja(dir_path, variables)


def initial_processing(top_dir_path):
    dir_content = [top_dir_path / p for p in os.listdir(top_dir_path)]
    logging.info(f"Processing top dir '{top_dir_path}'...")
    process_top_dir(top_dir_path)
    for path in dir_content:
        if path.is_dir():
            logging.info(f"Processing project '{path.name}'...")
            process_prj_dir(path)


class EventHandler(FileSystemEventHandler):
    def __init__(self, top_dir_path, handler_prj, handler_ver):
        self.top_dir_path = top_dir_path
        self.top_dir_path_abs = self.top_dir_path.expanduser().absolute()
        self.handler_prj = handler_prj
        self.handler_ver = handler_ver
        super().__init__()

    def is_prj_dir(self, dir_path_abs):
        return dir_path_abs is not None and \
               self.top_dir_path_abs == dir_path_abs.parent and \
               not dir_path_abs.name.startswith('_')

    def is_ver_dir(self, dir_path_abs):
        return dir_path_abs is not None and \
               self.top_dir_path_abs == dir_path_abs.parent.parent and \
               not dir_path_abs.parent.name.startswith('_') and \
               semver.validate(dir_path_abs.name)

    def handle_path(self, path):
        path_abs = Path(path).expanduser().absolute()
        path_rel = str(path_abs.relative_to(self.top_dir_path_abs))

        if self.is_prj_dir(path_abs):
            logging.info(f"Project '{path_rel}' added/removed")
            self.handler_prj(path_abs)
        elif self.is_ver_dir(path_abs):
            logging.info(f"Version '{path_rel}' added/removed")
            self.handler_ver(path_abs)

    def on_any_event(self, event):
        if event.is_directory and not event.event_type == 'modified':
            self.handle_path(event.src_path)
            if hasattr(event, 'dest_path'):
                self.handle_path(event.dest_path)


class Monitor():
    def __init__(self, top_dir_path, handler_prj, handler_ver):
        self.top_dir_path = top_dir_path
        event_handler = EventHandler(top_dir_path, handler_prj, handler_ver)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(top_dir_path), recursive=True)

    def start(self):
        logging.info(f"Monitoring '{self.top_dir_path}'...")
        self.observer.start()

    def stop(self):
        logging.info("Stopping Monitor...")
        self.observer.stop()
        self.observer.join()


def setup_logging():
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y/%m/%d %H:%M:%S', level=logging.INFO)

class StopGuard:
    def __init__(self):
        self.stop_event = Event()
        def signal_handler(signal, frame):
            self.stop_event.set()
        signal.signal(signal.SIGINT, signal_handler)

    def wait(self):
        self.stop_event.wait()
        logging.info("Stopping application...")


class Worker(Thread):
    CMD_CONT = 0
    CMD_STOP = 1

    def __init__(self, guard_time):
        self.queue = Queue()
        self.command = Queue(1)
        self.guard_time = guard_time
        super().__init__()

    def schedule(self, item=None):
        self.queue.put(item)
        try:
            self.command.put_nowait(self.CMD_CONT)
        except queue.Full:
            pass

    def run(self):
        try:
            while True:
                if self.command.get() == self.CMD_STOP:
                    break
                elements = []
                while True:
                    try:
                        element = self.queue.get(timeout=self.guard_time)
                        elements.append(element)
                    except queue.Empty:
                        break
                if elements:
                    self.task(elements)
        except:
            os.kill(os.getpid(), signal.SIGINT)

    def stop(self):
        logging.info(f"Stopping {self.__class__.__name__}...")
        self.command.put(self.CMD_STOP)
        self.join()


class WorkerPrj(Worker):
    def task(self, items):
        # should have always at least element
        if items:
            logging.info('Refreshing top dir...')
            top_dir_path = items[0].parent
            process_top_dir(top_dir_path)


class WorkerVer(Worker):
    def task(self, items):
        project_paths = {i.parent for i in items if i.parent.is_dir()}
        for project_path in project_paths:
            logging.info(f"Refreshing project '{project_path.name}'")
            process_prj_dir(project_path)


def main():
    repo = len(sys.argv) > 1 and sys.argv[1] or 'repo'
    guard_time = len(sys.argv) > 2 and int(sys.argv[2]) or 1

    top_dir_path = Path(repo)
    setup_logging()


    worker_prj = WorkerPrj(guard_time)
    worker_ver = WorkerVer(guard_time)

    initial_processing(top_dir_path)
    mointor = Monitor(top_dir_path, worker_prj.schedule, worker_ver.schedule)

    threads = [worker_prj, worker_ver, mointor]

    stop_guard = StopGuard()

    for t in threads:
        t.start()

    stop_guard.wait()

    for t in threads:
        t.stop()

    logging.info("Bye!")


if __name__ == "__main__":
    main()

