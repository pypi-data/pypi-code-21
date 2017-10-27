# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

""" Agent Module handles communication and instrumentation, this
is the main class.
"""

from __future__ import unicode_literals

import threading
import os
import logging

from queue import Queue, Full

from tcell_agent.agent import TCellAgent, PolicyTypes

LOGGER = logging.getLogger('tcell_agent').getChild(__name__)

appsensorLock = threading.Lock()


def run_appsensor(appsensor_meta):
    appsensor_policy = TCellAgent.get_policy(PolicyTypes.APPSENSOR)
    if appsensor_meta is None or appsensor_policy is None:
        return

    appsensor_policy.process_appsensor_meta(appsensor_meta)


class AppSensorManager(object):
    def __init__(self):
        self._appsensor_thread = None
        self._appsensor_thread_pid = os.getpid()
        self._appsensor_queue = Queue(100)
        self.use_threads = True

    def ensure_appsensor_thread_running(self):
        if self.is_appsensor_thread_running():
            return
        appsensorLock.acquire()
        try:
            if self.is_appsensor_thread_running():
                return
            self.start_appsensor_thread()
        finally:
            appsensorLock.release()

    def is_appsensor_thread_running(self):
        return self._appsensor_thread and self._appsensor_thread.isAlive() and self._appsensor_thread_pid == os.getpid()

    def start_appsensor_thread(self):
        """Start the background threads for polling/events"""

        def run_appsensor_thread():
            while True:
                metadata = self._appsensor_queue.get(True)
                try:
                    if metadata:
                        run_appsensor(metadata)
                except Exception as e:
                    LOGGER.error("Exception running appsensor: {e}".format(e=e))
                    LOGGER.debug(e, exc_info=True)

        self._appsensor_thread = threading.Thread(target=run_appsensor_thread, args=())
        self._appsensor_thread.daemon = True  # Daemonize thread
        self._appsensor_thread.start()
        self._appsensor_thread_pid = os.getpid()

    def send_appsensor_data(self, appsensor_meta_data):
        if appsensor_meta_data is None:
            return

        if self.use_threads is False:
            run_appsensor(appsensor_meta_data)
        else:
            self.ensure_appsensor_thread_running()
            try:
                self._appsensor_queue.put_nowait(appsensor_meta_data)
            except Full:
                LOGGER.debug("Appsensor queue full")


app_sensor_manager = AppSensorManager()
