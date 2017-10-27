# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

""" Agent Module handles communication and instrumentation, this
is the main class.
"""

from __future__ import unicode_literals
from __future__ import print_function

import os
import time

try:
    import cPickle as pickle
except:
    import pickle

import struct

import threading

import logging

LOGGER = logging.getLogger('tcell_agent').getChild(__name__)


class ForkPipeManager(object):
    def __init__(self, callback=None):
        self.callback = callback
        self.readp, self.writep = os.pipe()
        self.wr = os.fdopen(self.writep, 'wb', 0)
        self.pipe_running = False
        self.polling_thread = threading.Thread(target=self.run, args=())
        self.polling_thread.daemon = True  # Daemonize thread
        self.polling_thread.start()

    def run(self):
        try:
            r = os.fdopen(self.readp, 'rb')
            self.pipe_running = True
            LOGGER.debug("Parent Thread Starting Listen loop {pid}".format(pid=os.getpid()))
            while True:
                try:
                    LOGGER.debug("Parent Thread Waiting to read object {pid}".format(pid=os.getpid()))
                    pickled_obj_byte_len = r.read(4)
                    length = struct.unpack(">I", pickled_obj_byte_len)[0]
                    pickled_obj = r.read(length)
                    value = pickle.loads(pickled_obj)
                    if self.callback:
                        self.callback(value)
                except EOFError as eofe:
                    LOGGER.error("Parent Thread eof exception in pipe read: {e}".format(e=eofe))
                    LOGGER.debug(eofe, exc_info=True)
                    time.sleep(1.0)
                except Exception as eee:
                    LOGGER.error("Parent Thread exception in pipe read: {e}".format(e=eee))
                    LOGGER.debug(eee, exc_info=True)
                    time.sleep(1.0)
        except Exception as e:
            LOGGER.error("Parent Thread general exception in pipe read: {e}".format(e=e))
            LOGGER.debug(e, exc_info=True)
        finally:
            self.pipe_running = False

    def send_to_parent(self, obj):
        try:
            LOGGER.debug("Fork sending to parent {pid} {status}".format(pid=os.getpid(), status=self.pipe_running))
            if self.pipe_running:
                pickled_obj = pickle.dumps(obj)
                # if sys.version_info >= (3, 0):
                #    pickled_obj = unicode(pickled_obj)
                pickled_obj_byte_len = struct.pack(">I", len(pickled_obj))
                self.wr.write(pickled_obj_byte_len + pickled_obj)
            else:
                LOGGER.debug("POSSIBLE ISSUE: fork not running.")
                return False
        except Exception as e:
            LOGGER.error("exception sending to parent pipe: {e}".format(e=e))
            LOGGER.debug(e, exc_info=True)
            return False
        return True
