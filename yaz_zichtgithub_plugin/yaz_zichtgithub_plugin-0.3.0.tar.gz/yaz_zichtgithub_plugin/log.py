"""Logging configuration."""

import logging

__all__ = ["logger", "set_verbose"]

# Name the logger after the package.
logger = logging.getLogger(__package__)

def set_verbose(verbose: bool):
    """Set the logging level to INFO when VERBOSE"""
    if verbose:
        logging.basicConfig(level=logging.INFO)

        try:
            import coloredlogs
            coloredlogs.install(level="INFO")
        except:
            pass
