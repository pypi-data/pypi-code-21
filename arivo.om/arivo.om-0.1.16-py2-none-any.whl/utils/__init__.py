import logging

from .config import log_level as __log_level


def setup_logging():
    log_level = __log_level()
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s:%(levelname)s:%(name)s -> %(message)s [%(filename)s:%(lineno)s]"
    )
