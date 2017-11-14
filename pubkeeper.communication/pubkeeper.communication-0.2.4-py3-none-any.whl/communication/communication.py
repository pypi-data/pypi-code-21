"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from tornado.locks import Event
from tornado import ioloop
import logging


class PubkeeperCommunication(object):
    default_config = {}

    def __init__(self, config, *args, **kwargs):  # pragma: no cover
        self.logger = logging.getLogger('pubkeeper.communication.{}'.format(
            self.__class__.__name__
        ))

        self._running = Event()
        self.config = {}
        self._parse_config(config)

        super().__init__(*args, **kwargs)

    def _parse_config(self, config):
        self.config = self.default_config.copy()
        self.config['_parsed_'] = True

        non_casting_types = [type(None), str]
        for key in self.config.keys():
            if key in config:
                _type = type(self.config[key])
                if _type in non_casting_types:
                    self.config[key] = config[key]
                else:
                    self.config[key] = _type(config[key])

    def start(self, io_loop=None):  # pragma: no cover
        if io_loop is None:
            self._ioloop = ioloop.IOLoop.current()
        else:
            self._ioloop = io_loop

        self._running.set()

    def shutdown(self):  # pragma: no cover
        self._running.clear()
