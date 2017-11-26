"""
Journal & debugging
Repris de http://sametmax.com/ecrire-des-logs-en-python/

On log dans la console et dans le fichier défini dans la configuration
"""

import logging
from logging.handlers import RotatingFileHandler

from . import settings

# pylint: disable=C0103
logger = logging.getLogger()
logger.setLevel(getattr(logging, settings.LOGGER_LEVEL))

# pylint: disable=C0103
if settings.LOGGER_PATH:
    formatter = logging.Formatter(
        '%(asctime)s :: %(levelname)s :: %(message)s')
    file_handler = RotatingFileHandler(settings.LOGGER_PATH, 'a', 1000000, 1)
    file_handler.setLevel(getattr(logging, settings.LOGGER_LEVEL))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# pylint: disable=C0103
stream_handler = logging.StreamHandler()
stream_handler.setLevel(getattr(logging, settings.LOGGER_LEVEL))
logger.addHandler(stream_handler)
