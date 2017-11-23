import os
import logging
import pathlib

import daiquiri

LOGDIR = pathlib.Path.home() / '.logs'


def Logger(name=None, level=logging.INFO):
    if not LOGDIR.exists():
        LOGDIR.mkdir(parents=True)

    daiquiri.setup(outputs=(
        daiquiri.output.STDERR,
        daiquiri.output.File(directory=LOGDIR)
    ), level=level)

    logger = daiquiri.getLogger(name)

    if os.getenv('DEBUG'):
        logger.setLevel(logging.DEBUG)

    return logger
