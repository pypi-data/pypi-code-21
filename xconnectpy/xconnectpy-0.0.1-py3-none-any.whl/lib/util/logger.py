#!/usr/bin/python

import logging
import sys


class Logger:

    def __init__(self, enable_log=True, log_file="logs/log.txt"):
        self.enable_log = enable_log
        self.log_file = log_file

        try:
            if enable_log:
                if log_file:
                    logging.basicConfig(filename=log_file, format='%(asctime)s %(message)s',
                                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
                else:
                    logging.basicConfig(format='%(asctime)s %(message)s',
                                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

                self.info('Logger initialized.')

        except Exception:
            print('Error initializing logger.', sys.exc_info()[0])
            sys.exit(1)

    def info(self, msg):
        if self.enable_log:
            logging.info(msg)

    def warning(self, msg):
        if self.enable_log:
            logging.info(msg)

    def error(self, msg):
        if self.enable_log:
            logging.error(msg)
