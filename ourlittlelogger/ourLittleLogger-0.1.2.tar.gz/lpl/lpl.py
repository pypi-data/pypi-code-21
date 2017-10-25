"""Logger for connectome python projects."""
import logging

def getLogger(module_name='connectome_module'):
    """Get logger with specified logger name."""
    fmt = '%(asctime)s.%(msecs)03d | %(name)s | [%(levelname)s]: %(message)s'
    datefmt = '%d-%m-%Y %H:%M:%S'
    logging.basicConfig(level=logging.DEBUG, format=fmt, datefmt=datefmt)
    logger = logging.getLogger(module_name)
    return logger
