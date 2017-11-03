#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import shutil
import datetime
import warnings
import better_exceptions
from logging import *
from types import MethodType
from tempfile import gettempdir
from inspect import stack, getmodule

u"""
set_up_basic_logging function configures the log file
to use and the logging level.

The global 'logging_file' is used to prevent the config
being set more than once.
"""

better_exceptions.MAX_LENGTH = None

LOG_FOLDER_PATH = None  # Set this to initialise a specific log file path.  If None LOG_FOLDER_TEMP_PATH is used.
LOG_FOLDER_TEMP_PATH = u'{p}{sep}{d}'.format(p=gettempdir(),
                                             sep=os.sep,
                                             d=u'logs')

# Setup logger for this helper (note will log out to whatever you setup).
logging_handler_logger = getLogger(__name__)


class LHFileHandler(FileHandler):

    def __init__(self,
                 name):

        self._datestamp = datetime.datetime.now().strftime(u'%Y-%m-%d %H%M%S')

        FileHandler.__init__(self,
                             filename=self._create_base_file_name(LOG_FOLDER_TEMP_PATH, name=name),
                             encoding=u'UTF8')

        self.set_name(name)

    def _create_base_file_name(self,
                               pth,
                               name=None):

        dirname = self.get_name() if name is None else name

        fn = u'{filename} {date}.log'.format(filename=dirname,
                                             date=self._datestamp)

        new_filepath = u'{logs_folder}{sep}{sub_folder}{sep}'.format(logs_folder=pth,
                                                                     sub_folder=dirname,
                                                                     sep=os.sep)

        ensure_path_exists(new_filepath)

        return os.path.abspath(u'{p}{sep}{n}'.format(p=new_filepath,
                                                     sep=os.sep,
                                                     n=fn))

    def set_path(self,
                 filepath):

        """
        Allows you to update the log file location, moving the existing log file to the new path.

        :param filepath: Path to move log file to.
        """

        # Get existing file handler settings
        old_filepath = self.baseFilename
        new_filepath = self._create_base_file_name(filepath)

        # We are updating a shared resource to lets acquire a lock
        self.acquire()

        try:
            logging_handler_logger.debug(u'Setting log file path to: {p}'.format(p=new_filepath))

            # Set the new file path
            self.baseFilename = new_filepath

            # Flush & close existing stream
            if self.stream:
                try:
                    self.flush()

                finally:
                    stream = self.stream
                    self.stream = None
                    if hasattr(stream, "close"):
                        stream.close()

            # Move log file to new location
            shutil.move(old_filepath, new_filepath)

            logging_handler_logger.info(u'Log file path set to: {p}'.format(p=self.baseFilename))

        finally:
            self.release()


# Logging Helper Functions

def ensure_path_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def setup_log_format(date_format=u'%Y-%m-%d %H:%M:%S'):

    # Setup formatter to define format of log messages
    format_string = u'{timestamp} - {level} - {name} : {msg}'.format(timestamp=u'%(asctime)s',
                                                                     level=u'%(levelname)-7s',
                                                                     name=u'%(name)-45s',
                                                                     msg=u'%(message)s')

    log_formatter = Formatter(fmt=format_string,
                              datefmt=date_format)

    return log_formatter


def check_for_main():

    name = get_caller_name(level=3)
    logging_handler_logger.debug(u'Check Main: {c}'.format(c=name))

    return name == u'__main__' or name.endswith(u'__main__')


def get_caller_filename(level=2):

    path = stack()[level][1]
    filename = path.split(u'/')[-1]
    filename = filename.replace(u'.py', u'')

    logging_handler_logger.debug(u'Caller Filename: {c}'.format(c=filename))

    return filename


def get_caller_name(level=2):

    frame = stack()[level][0]
    module = getmodule(frame)

    if module is None:
        name = None

        if frame.f_locals is not None:
            name = frame.f_locals.get(u'__name__')

        if name is None:
            name = u'Cannot get __name__, filename: {fn}'.format(fn=get_caller_filename(level=3))

    else:
        name = module.__name__

    logging_handler_logger.debug(u'Caller Name: {c}'.format(c=name))

    return name


# New logger methods (these are added to the logger in setup_logging function

def __lh_setup_file_handler(self,
                            filename,
                            filepath=LOG_FOLDER_PATH,
                            level=NOTSET):

    if self.LH_FILE_HANDLER is None:
        # Update the filename for the root logger if required
        filename = u'Root_logger' if filename in (u'', u'__main__') else filename

        self.LH_FILE_HANDLER = LHFileHandler(name=filename)
        self.LH_FILE_HANDLER.setFormatter(setup_log_format())
        self.LH_FILE_HANDLER.setLevel(level=level)

        self.addHandler(self.LH_FILE_HANDLER)

        logging_handler_logger.info(u'Logging to file')

        if filepath is not None:
            self.LH_FILE_HANDLER.set_path(filepath=filepath)

    else:
        logging_handler_logger.warning(u'Not setting up file handler, handler already setup')


def __lh_setup_console_handler(self,
                               level=NOTSET):

    if self.LH_CONSOLE_HANDLER is None:
        self.LH_CONSOLE_HANDLER = StreamHandler()
        self.LH_CONSOLE_HANDLER.setFormatter(setup_log_format())
        self.LH_CONSOLE_HANDLER.setLevel(level=level)

        self.addHandler(self.LH_CONSOLE_HANDLER)
        logging_handler_logger.info(u'Logging to console')

    else:
        logging_handler_logger.warning(u'Not setting up console handler, handler already setup for logger')


def __lh_set_file_level(self,
                        level):
    self.LH_FILE_HANDLER.setLevel(level)


def __lh_set_console_level(self,
                           level):
    self.LH_CONSOLE_HANDLER.setLevel(level)


def __lh_set_level(self,
                   level,
                   handler=None):

    if handler is not None:
        handler.setLevel(level)

    else:
        self._oldSetLevel(level)


# Logging setup function - use this to setup logging in your modules

def setup_logging(logger_name=None,
                  level=NOTSET,
                  log_to_file=True,
                  log_to_console=True,
                  capture_warnings=True):

    """
    Eases setup of logging to file and console

    @param logger_name:         Name of logger.  This will also be used for file/folder name
                                DEFAULT: name of calling module
    @param level:               Log level to be used.
                                DEFAULT: logging.NOTSET
    @param log_to_file:         Enable/Disable logging to file.
                                DEFAULT: True
    @param log_to_console:      Enable/Disable logging to console.
                                DEFAULT: True
    @param capture_warnings:    Enable/Disable logging of warnings from warning module.
                                DEFAULT: True
    @return:                    Returns the configured logger.
    """

    if not logger_name:
        logger_name = get_caller_name()

    # Get the logger
    if logger_name == u'__main__' or check_for_main():

        if logger_name == u'__main__':
            logger_name = u'Root Logger'

        logger = getLogger()
        logger.setLevel(NOTSET)  # Root logger level is set for individual handlers

        logger.name = logger_name
        setup_handlers = True

        # Tell logging to handle warnings from the warnings module
        if capture_warnings:
            # Enable logging or warnings raised in the warnings module
            captureWarnings(True)

            # Remove default python warning module filters (we want deprecation & import warnings)
            warnings.resetwarnings()

    else:
        logger = getLogger(logger_name)
        logger.setLevel(level)  # Non-root loggers can set their own level (this will be limited by the root logger)
        setup_handlers = False

    # Setup handler attributes & methods
    if not hasattr(logger, u'LH_CONSOLE_HANDLER'):
        logger.LH_CONSOLE_HANDLER = None

    if not hasattr(logger, u'LH_FILE_HANDLER'):
        logger.LH_FILE_HANDLER = None

    if u'lh_setup_console_handler' not in dir(logger):
        logger.lh_setup_console_handler = MethodType(__lh_setup_console_handler, logger)

    if u'lh_setup_file_handler' not in dir(logger):
        logger.lh_setup_file_handler = MethodType(__lh_setup_file_handler, logger)

    if u'__lh_set_console_level' not in dir(logger):
        logger.lh_set_console_level = MethodType(__lh_set_console_level, logger)

    if u'__lh_set_file_level' not in dir(logger):
        logger.lh_set_file_level = MethodType(__lh_set_file_level, logger)

    if u'_oldSetLevel' not in dir(logger):
        logger._oldSetLevel = logger.setLevel
        logger.setLevel = MethodType(__lh_set_level, logger)

    if setup_handlers:
        if log_to_console:
            logger.lh_setup_console_handler(level=level if log_to_console is True else log_to_console)

        if log_to_file:
            logger.lh_setup_file_handler(filename=logger_name,
                                         level=level if log_to_file is True else log_to_file)

    return logger


if __name__ == u'__main__':
    # TODO: Add these to unittests!
    logtest = setup_logging(logger_name=u'TESTING HELPER', level=DEBUG, log_to_file=True)
    logtest.debug(u'Test log message 1')
    logtest.lh_set_console_level(INFO)
    logtest.debug(u'Test log message 2')  # This message should not display
    logtest.lh_set_console_level(DEBUG)
    logtest.debug(u'Test log message 3')
    logtest.setLevel(INFO, logtest.LH_CONSOLE_HANDLER)  # this is the same as logtest.lh_set_console_level(INFO)
    logtest.debug(u'Test log message 4')  # This message should not display
    logtest.setLevel(DEBUG, logtest.LH_CONSOLE_HANDLER)  # this is the same as logtest.lh_set_console_level(DEBUG)
    logtest.debug(u'Test log message 5')
    logtest.setLevel(WARN)  # This sets the root logger level
    logtest.debug(u'Test log message 6')  # This message should not display
    logtest.setLevel(DEBUG)
    logtest.debug(u'Test log message 7')
    logtest.LH_FILE_HANDLER.set_path(u'{p}{sep}{d}'.format(p=gettempdir(),
                                                           sep=os.sep,
                                                           d=u'logs2'))
    logtest.debug(u'Test log message 8')
    logtest.debug(u'Test log message 9')
