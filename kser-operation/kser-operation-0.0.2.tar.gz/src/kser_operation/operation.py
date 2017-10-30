#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging
from uuid import uuid4

from cdumay_result import Result
from kser.transport import Message

logger = logging.getLogger(__name__)


class Operation(object):
    """"""

    @classmethod
    def init_by_id(cls, _id):
        """Load operation by its ID

        :param Any _id: Operation ID
        :return: the operation
        :rtype: kser_operation.operation.Operation
        """

    def __init__(self, uuid=None, status="PENDING", tasks=None, **kwargs):
        self.uuid = uuid or str(uuid4())
        self.tasks = tasks or list()
        self.status = status
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return "Operation [{}](id={},status={})".format(
            self.__class__.__name__, self.uuid, self.status
        )

    def get_attr(self, item):
        attr = "{}Id".format(item)
        return attr, getattr(getattr(self, item, self), attr, None)

    def _set_status(self, status):
        """ update operation status

        :param str status: New status
        """
        logger.info("Operation {}[{}] status update '{}' -> '{}'".format(
            self.__class__.__name__, self.uuid, self.status, status
        ))
        return self.set_status(status)

    def set_status(self, status):
        """ update operation status

        :param str status: New status
        """
        self.status = status

    def add_task(self, task):
        """ add task to operation

        :param kser_operation.task.Task task: task to add
        """
        self.tasks.append(task)

    def _prerun(self):
        """ To execute before running message
        """
        self._set_status("RUNNING")
        logger.info("Operation {}[{}] started".format(
            self.__class__.__name__, self.uuid
        ))
        return self.prerun()

    def prerun(self):
        """ To implement, perform check before operation run
        """

    def _onsuccess(self, result):
        """ To execute on execution success
        :param cdumay_result.Result result: Execution result
        :return: Execution result
        :rtype: cdumay_result.Result
        """
        self._set_status("SUCCESS")
        logger.info("Operation {}[{}] Success: {}".format(
            self.__class__.__name__, self.uuid, result
        ))
        return self.onsuccess(result)

    def onsuccess(self, result):
        """ To implement on execution success

        :param cdumay_result.Result result: Execution result
        :return: Execution result
        :rtype: cdumay_result.Result
        """
        return result

    def _onerror(self, result):
        """ To execute on execution failure

        :param kser.transport.Message kmsg: Kafka message
        :param cdumay_result.Result result: Execution result
        :return: Execution result
        :rtype: cdumay_result.Result
        """
        self._set_status("FAILED")
        logger.error("Operation {}[{}] Failed: {}".format(
            self.__class__.__name__, self.uuid, result
        ))
        return self.onerror(result)

    def onerror(self, result):
        """ To implement on execution failure

        :param cdumay_result.Result result: Execution result
        :return: Execution result
        :rtype: cdumay_result.Result
        """
        return result

    def to_kmsg(self):
        """Convert operation to Kser Message

        :return: The Kser operation
        :rtype: kser.transport.Message
        """
        return Message(
            uuid=str(self.uuid),
            entrypoint="OperationLauncher",
            params=dict(_id=str(self.uuid))
        )

    def execute(self):
        """ Execution 'wrapper' to make sure that it return a result

        :return: Execution result
        :rtype: cdumay_result.Result
        """
        self._prerun()
        try:
            result = None
            for task in self.tasks:
                result = task.execute()

            return self._onsuccess(result + Result(
                uuid=str(self.uuid),
                stdout="Operation {}[{}] successed".format(
                    self.__class__.__name__, self.uuid
                )
            ))

        except Exception as exc:
            return self._onerror(
                Result.fromException(exc, str(self.uuid))
            )

    def display(self):
        """ dump operation

        """
        print("{}".format(self))
        for task in self.tasks:
            print("  - {}".format(task))

    def next(self, task):
        for idx, otask in enumerate(self.tasks[:-1]):
            if otask.uuid == task.uuid:
                return self.tasks[idx + 1]

    def launch_next(self, task=None, result=None):
        """ Launch next task or finish operation

        :param kser_operation.task.Task task: previous task
        :param cdumay_result.Result result: previous task result

        :return: Execution result
        :rtype: cdumay_result.Result
        """
        if task:
            next = self.next(task)
            if next:
                return next.send(result=result)
            else:
                return self.set_status(task.status)
        elif len(self.tasks) > 0:
            return self.tasks[0].send(result=result)
        else:
            return Result(retcode=1, stderr="Nothing to do, empty operation !")

    def launch(self):
        """ Send the first task

        :return: Execution result
        :rtype: cdumay_result.Result
        """
        return self.launch_next()

    def finalize(self):
        """To implement, post build actions (database mapping ect...)

        :return: the controller
        :rtype: kser_operation.operation.Operation
        """
        return self
