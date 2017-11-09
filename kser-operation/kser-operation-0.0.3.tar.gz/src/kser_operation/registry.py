#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging

from kser.controller import Controller
from kser.entry import Entrypoint

logger = logging.getLogger(__name__)


class OperationRegistry(object):
    def __init__(self, app=None):
        self.controller = Controller()
        self.app = None
        if app:
            self.init_app(app)

    def load_module(self, module):
        for value in vars(module).values():
            try:
                if issubclass(value, Entrypoint) and (value != Entrypoint):
                    self.controller.register(value)
            except:
                pass

    def register(self, entrypoint):
        """Shortcut to registry registration"""
        logger.info("Operation registry: loaded {}".format(entrypoint.path))
        self.controller.register(entrypoint.path, entrypoint)

    def init_app(self, app=None):
        self.app = app
        self.load_tasks()

    def load_tasks(self):
        """ To implement, load operation tasks

        :return:
        """
