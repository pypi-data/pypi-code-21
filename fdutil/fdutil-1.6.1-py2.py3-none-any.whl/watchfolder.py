#!/usr/bin/python

import os
import time
from Queue import Queue, Empty  # change this to from queue and its Python 3 ready!
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool

from list_tools import filter_list
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from watchdog.observers import Observer

import logging_helper

__author__ = "Oli Davis"
__copyright__ = "Copyright (C) 2016 Oli Davis"

logging = logging_helper.setup_logging()


class WatchFolderEventHandler(FileSystemEventHandler):
    """Monitor for File creation events."""

    def __init__(self):
        self.incoming_queue = Queue()

    def on_created(self, event):
        super(WatchFolderEventHandler, self).on_created(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info('Created {w}: {p}'.format(w=what,
                                               p=event.src_path))

        if not event.is_directory:
            if not (event.src_path.split(os.sep)).pop()[0] == '.':
                self.incoming_queue.put(event)


class WatchIncomingFileQueue(object):

    # TODO: Filter out any files not specified i.e only accept .txt files
    def __init__(self,
                 path,
                 recursive=True,
                 load_existing=True,
                 threads=cpu_count()):

        """

        :param path:            Path of folder to be watched
        :param recursive:       Defines whether subfolders should be observed recursively
        :param load_existing:    If True loads any existing files from path to queue
        :param threads:         Number of worker threads (minimum 2). If not specified then os.cpu_count() is used
        """

        # Setup passed params
        self.path = path
        self.recursive = recursive
        self.load_existing = load_existing
        self.pool = ThreadPool(processes=threads if threads > 1 else 2)

        self.__stop = True
        self.ready_queue = Queue()

        # Create event handler
        self.event_handler = WatchFolderEventHandler()

        # Create WatchDog Observer
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.path, recursive=self.recursive)

    def start(self):

        logging.info('Starting Incoming File Watcher...')

        # Set flag to allow loop activation
        self.__stop = False

        # Load existing files in folder
        if self.load_existing:

            files = os.listdir(self.path)
            filtered_list = filter_list(item_list=files, filters=[], exclude=True)

            # TODO: Make this work recursively!
            for file in filtered_list:

                file_path = '{p}{s}{f}'.format(p=self.path,
                                               s=os.sep,
                                               f=file)

                self.event_handler.incoming_queue.put(file_path)
                logging.info('Existing file: {f}'.format(f=file_path))

        self.observer.start()

        logging.info(u'Incoming File Watcher Started')

        # Run Main loop
        self.pool.apply_async(func=self.__main_loop)

    def __main_loop(self):

        while not self.__stop:

            # Get next item from queue or wait for an item to be added
            try:
                item = self.event_handler.incoming_queue.get(timeout=5)

            except Empty:
                continue

            if type(item) is FileCreatedEvent:
                item = item.src_path

            # Pass item to worker thread
            self.pool.apply_async(func=self.__worker,
                                  kwds={'path': item})

    def stop(self):

        logging.info('Stopping Incoming File Watcher, waiting for processes to complete...')

        # Signal loop termination
        self.__stop = True

        # Stop the watch folder observer
        self.observer.stop()
        self.observer.join()

        # Wait for running processes to complete
        self.pool.close()
        self.pool.join()

        logging.info('Incoming File Watcher Stopped')

    @staticmethod
    def check_copy_completion(path):

        """
        Watch file at path until its size stops changing.
        NOTE: Cannot account for partial copies!

        :param path: Path to file
        :return: True when copy completes
                 False if file gets removed before completion
        """

        logging.info('Waiting on copy completion for {p}'.format(p=path))

        try:
            last_size = os.path.getsize(path)
            logging.debug('Initial size: {s} - {p}'.format(s=last_size,
                                                           p=path))
            time.sleep(1)  # Ensure file size has a chance to change.

            while True:
                current_size = os.path.getsize(path)

                logging.debug('Check size: {s} - {p}'.format(s=current_size,
                                                             p=path))

                if last_size == current_size:
                    logging.info('Copy complete for {p}'.format(p=path))
                    return True

                last_size = current_size

                time.sleep(10)

        except os.error as err:
            logging.error(err)
            return False

    def __worker(self, path):

        try:
            # Wait for copy to complete
            copy_status = self.check_copy_completion(path=path)

            # If copy successful add path to ready_queue
            if copy_status:
                self.ready_queue.put(path)

        except Exception as err:
            logging.error('Something went wrong in worker!')
            logging.error(err)


def run_example_watchfolder(path):

    watcher = WatchIncomingFileQueue(path=path)

    try:
        watcher.start()

        while True:
            logging.debug('Ready: {f}'.format(f=watcher.ready_queue.get()))

    except KeyboardInterrupt:
        watcher.stop()


if __name__ == "__main__":
    run_example_watchfolder(path='/Users/davisowb/Desktop/Watchfolder')
