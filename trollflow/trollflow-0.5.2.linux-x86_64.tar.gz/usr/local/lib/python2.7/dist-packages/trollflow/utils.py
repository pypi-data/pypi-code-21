import importlib
import logging
from collections import OrderedDict
import yaml
from threading import ThreadError

logger = logging.getLogger(__name__)


def get_class(clazz_path):
    parts = clazz_path.split('.')
    module_name = ".".join(parts[:-1])
    clazz_name = parts[-1]
    module = importlib.import_module(module_name)
    clazz = getattr(module, clazz_name)
    logger.info("Initialized %s", str(clazz))
    return clazz


def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def stop_worker(worker, flush_queue=True):
    """Stop the given worker and join all the queues"""
    try:
        worker.stop()
    except AttributeError:
        pass
    try:
        if flush_queue:
            if worker.input_queue.qsize() > 0:
                logger.debug("Flushing %d items from input queue",
                             worker.input_queue.qsize())
                # Make sure that all items have been cleared
                while worker.input_queue.qsize() > 0:
                    itm = worker.input_queue.get()
                    worker.input_queue.task_done()
                    del itm
            logger.debug("Joining input queue")
            worker.input_queue.join()
    except (AttributeError, ValueError):
        pass


def release_lock(lock):
    """Release the lock of the previous step."""
    if lock is not None:
        try:
            lock.release()
            logger.debug("Released lock %s", str(lock))
            return True
        except (ThreadError, RuntimeError):
            return False


def acquire_lock(lock):
    """Acquire lock and wait for its release"""
    if lock is not None:
        lock.acquire(True)
        logger.debug("Acquired lock %s", str(lock))
        return True
    return False
