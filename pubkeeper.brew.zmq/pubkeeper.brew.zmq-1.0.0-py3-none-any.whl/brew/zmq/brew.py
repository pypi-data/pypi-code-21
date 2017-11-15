"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from enum import IntEnum

from pubkeeper.brew.base import Brew
from pubkeeper.utils.logging import get_logger

from pubkeeper.brew.zmq.driver import ZMQSettings
from pubkeeper.brew.zmq.driver.manager import ZMQManager


class ZMQBrew(Brew):

    class Status(IntEnum):
        created = 1
        configuring = 2
        configured = 3
        stopping = 4
        stopped = 5
        starting = 6
        started = 7
        warning = 8
        error = 9

    def __init__(self, *args, **kwargs):
        self.name = 'zmq'
        super().__init__(*args, **kwargs)

        self._status = None
        self.logger = get_logger(self.__class__.__name__)

        self._zmq = ZMQManager()

        self._brewing = {}
        self._listening = {}
        self.status = ZMQBrew.Status.created

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self.logger.info("Setting status to {}".format(status.name))
        self._status = status

    @classmethod
    def get_settings(cls):
        return ZMQSettings

    def configure(self, context):
        self.status = ZMQBrew.Status.configuring
        self._zmq.configure(context)
        self.status = ZMQBrew.Status.configured

    def start(self):
        self.status = ZMQBrew.Status.starting
        self._zmq.start()
        self.status = ZMQBrew.Status.started

    def stop(self):
        self.status = ZMQBrew.Status.stopping
        # let manager close queues and listeners
        self._zmq.stop()

        # cleanup brewing and listening since resources were deallocated
        # by zmq.stop
        self._brewing = {}
        self._listening = {}

        self.status = ZMQBrew.Status.stopped

    def create_brewer(self, brewer):
        # a queue resource can be shared among the brewers with the same topic
        if brewer.brewer_id not in self._brewing:
            self._brewing[brewer.brewer_id] = self._zmq.create_queue()
            self.logger.info(
                "Created brewer for topic: '{}' at: {}".format(
                    brewer.topic,
                    self._brewing[brewer.brewer_id].publisher_url
                )
            )
        else:
            self.logger.debug(
                "A brewer for topic: '{}' already exists at: {}, reusing it".
                format(brewer.topic,
                       self._brewing[brewer.brewer_id].publisher_url)
            )

        return {
            'publisher_url': self._brewing[brewer.brewer_id].publisher_url
        }

    def destroy_brewer(self, brewer):
        if brewer.brewer_id in self._brewing:
            self._zmq.delete_queue(self._brewing[brewer.brewer_id])
            del self._brewing[brewer.brewer_id]

    def start_patron(self, patron_id, topic, brewer_id, brewer_config,
                     brewer_brew, callback):
        def _pk_callback_handler(data):
            callback(brewer_id, data)

        # create a unique key for given patron-brewer combination
        key = (patron_id, brewer_id)
        if key not in self._listening:
            self.logger.debug(
                "Start patron for patron_id: {} topic: '{}', reading from: {}".
                format(patron_id, topic, brewer_brew['publisher_url']))
            self._listening[key] = self._zmq.create_listener(
                brewer_brew['publisher_url'], _pk_callback_handler
            )
        else:
            self.logger.debug(
                "Patron: {} for topic: {} and brewer: {} is already started".
                format(patron_id, topic, brewer_id))

    def stop_patron(self, patron_id, topic, brewer_id):
        key = (patron_id, brewer_id)
        if key in self._listening:
            self.logger.debug("Stopping patron for patron_id: {}, topic: '{}'".
                              format(patron_id, topic))
            self._zmq.delete_listener(self._listening[key])
            del self._listening[key]
        else:
            self.logger.debug(
                "Patron: {} for topic: {} and brewer: {} is already stopped".
                format(patron_id, topic, brewer_id))

    def brew(self, brewer_id, topic, data, patrons):
        # zmq internally detects the presence or not of subscribers
        # and optimizes accordingly
        if self.status == ZMQBrew.Status.started:
            self._zmq.send(self._brewing[brewer_id], data)
