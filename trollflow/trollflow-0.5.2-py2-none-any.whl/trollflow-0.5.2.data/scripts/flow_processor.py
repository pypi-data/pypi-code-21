#!/usr/bin/python

"""Main script for trollflow based processors."""

import logging
import logging.config
import sys
import time
from threading import Lock
import os

from trollflow.workflow_streamer import WorkflowStreamer
from trollflow.utils import ordered_load, stop_worker, release_lock


def generate_daemon(config_item):
    """Return a daemon based on the YAML configuration"""
    logging.info("Starting daemon '%s'", config_item['name'])
    return config_item['components'][-1]['class']


def generate_thread_workflow(config_item, force_gc=False):
    wfs = WorkflowStreamer(config=config_item, force_gc=force_gc)
    wfs.setDaemon(True)
    wfs.start()
    return wfs


TYPES = {'daemon': generate_daemon,
         'workflow': generate_thread_workflow,
         }


def read_yaml_config(fname):
    """Read YAML config file"""
    # Read config
    with open(fname, "r") as fid:
        config = ordered_load(fid)

    return config


def setup_logging(config):
    """Setup logging"""

    # Check if log config is available, use it if it is
    if "log_config" in config["config"]:
        logging.config.fileConfig(config["config"]["log_config"],
                                  disable_existing_loggers=False)


def create_worker(item, force_gc=False):
    """Create a worker"""
    if item['type'] == 'workflow':
        return TYPES[item['type']](item, force_gc=force_gc)
    else:
        return TYPES[item['type']](item)


def create_threaded_workers(config):
    """Create workers"""

    workers = []
    try:
        force_gc = config["config"]["force_gc"]
        logging.info("Using forced garbage collection")
    except KeyError:
        force_gc = False

    for item in config['work']:
        workers.append(create_worker(item, force_gc=force_gc))

    queue = None
    prev_lock = None
    for worker in workers:
        if queue is not None:
            worker.input_queue = queue
        try:
            queue = worker.output_queue
        except AttributeError:
            queue = worker.queue

        try:
            worker.prev_lock = prev_lock
        except AttributeError:
            pass
        lock = Lock()
        try:
            worker.lock = lock
        except AttributeError:
            pass
        prev_lock = lock

    return workers


def find_dead_threads(workers, logger, config):
    """Check that all threads are alive, and try to reboot them if they've
    died."""
    for i, worker in enumerate(workers):
        # Check if the worker is dead
        try:
            is_alive = worker.is_alive()
        except AttributeError:
            is_alive = True

        if not is_alive:
            workers[i] = restart_dead_worker(logger, config, worker, i)
            release_lock(workers[i].prev_lock)
            release_lock(workers[i].lock)
            logger.info("Crashed worker restarted")


def restart_dead_worker(logger, config, worker, num):
    """Try to restart dead threads"""
    logger.error("Thread has crashed, trying to restart it")

    # Get existing linked queues and locks to safety
    input_queue = worker.input_queue
    output_queue = worker.output_queue

    prev_lock = worker.prev_lock
    lock = worker.lock

    try:
        worker.restart()
        logger.warning("Crashed daemon restarted")
    except AttributeError:
        try:
            force_gc = config["config"]["force_gc"]
        except KeyError:
            force_gc = False

        # Stop worker
        stop_worker(worker, flush_queue=False)

        # Create new worker
        item = find_worker_config_by_idx(config, num)
        logger.info("Starting %s", item['name'])
        worker = create_worker(item, force_gc=force_gc)

    # Link old queues and locks back to worker
    worker.input_queue = input_queue
    worker.output_queue = output_queue
    worker.prev_lock = prev_lock
    worker.lock = lock

    return worker


def find_worker_config_by_idx(config, num):
    """Find worker item config from master config by index number"""
    i = 0
    for item in config['work']:
        if i == num:
            return item
        i += 1


def wait_threads(workers, logger, config):
    """Loop workers until keyboard interrupt is detected, after which join
    the queues and stop the worker instances."""
    loop = True
    while loop:
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            logger.info("Closing flow processing items")
            for worker in workers:
                stop_worker(worker)
            loop = False
        else:
            find_dead_threads(workers, logger, config)


def main():
    """Main()"""

    config = read_yaml_config(sys.argv[1])

    try:
        if config["config"]["use_utc"]:
            os.environ["TZ"] = "UTC"
            time.tzset()
    except KeyError:
        pass

    setup_logging(config)
    logger = logging.getLogger("flow_processor")
    logger.info("Initializing flow processor")

    workers = create_threaded_workers(config)
    logger.info("Ready to process new data")
    wait_threads(workers, logger, config)

    logger.info("Flow processor has been shutdown.")

if __name__ == "__main__":
    main()
