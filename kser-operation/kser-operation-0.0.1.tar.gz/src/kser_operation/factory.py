#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging
from kser_operation.operation import Operation

logger = logging.getLogger(__name__)


class OperationController(object):
    @classmethod
    def new(cls, **kwargs):
        return cls(operation=Operation(**cls.parse_inputs(**kwargs)))

    @classmethod
    def parse_inputs(cls, **kwargs):
        return kwargs

    @classmethod
    def init_by_id(cls, _id, **kwargs):
        """Load operation by its ID"""
        return cls(operation=Operation.init_by_id(_id), **kwargs)

    def __init__(self, operation, **kwargs):
        self.operation = operation
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _prebuild(self, **kwargs):
        logger.debug("{}.PreBuild: {}".format(self.__class__.__name__, kwargs))
        return self.prebuild(**kwargs)

    def prebuild(self, **kwargs):
        """ to implement, perform check before the operation creation
        """

    def _build_tasks(self, **kwargs):
        """

        :param dict kwargs: tasks parameters (~=context)
        :return: list of tasks
        :rtype: list(kser_operation.operation.Operation)
        """
        tasks = self.build_tasks(**kwargs)
        logger.debug("{}.BuildTasks: {} task(s) found".format(
            self.__class__.__name__, len(tasks)
        ))
        return tasks

    def build_tasks(self, **kwargs):
        """

        :param dict kwargs: tasks parameters (~=context)
        :return: list of tasks
        :rtype: list(kser_operation.operation.Operation)
        """
        return list()

    def compute_tasks(self, **kwargs):
        params = self.prebuild(**kwargs) or kwargs
        return self.build_tasks(**params)

    def build(self, **kwargs):
        """ create the operation and associate tasks

        :param dict kwargs: operation data
        :return: the controller
        :rtype: kser_operation.controller.OperationController
        """
        self.operation.tasks += self.compute_tasks(**kwargs)
        return self.finalize()

    def finalize(self):
        """To implement, post build actions (database mapping ect...)

        :return: the controller
        :rtype: kser_operation.controller.OperationController
        """
        self.operation.finalize()
        return self

    def send(self):
        """ Send operation to Kafka
        
        :return: The operation
        :rtype: kser_operation.operation.Operation
        """
