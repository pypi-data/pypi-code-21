#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
from uuid import uuid4

from kser.entry import Entrypoint
from kser.transport import Message


class Task(Entrypoint):
    """"""

    def __init__(self, uuid=None, params=None, name=None, status="PENDING",
                 **kwargs):
        self.uuid = uuid or str(uuid4())
        self.params = params
        self.status = status
        self.path = name or self.__class__.path
        self.metadata = kwargs

    def get_attr(self, item):
        attr = "{}Id".format(item)
        return attr, getattr(getattr(self, item, self), attr, None)

    def to_kmsg(self, result=None):
        """Convert task to Kser Message

        :return: The Kser task
        :rtype: kser.transport.Message
        """
        return Message(
            uuid=str(self.uuid), entrypoint=self.path, params=self.params,
            result=result
        )

    def send(self, result=None):
        """ Send task to Kafka

        :param cdumay_result.Result result: previous task result
        :return: send response
        :rtype: cdumay_result.Result
        """

    def __repr__(self):
        return "Task [{}](uuid={},status={}, params={})".format(
            self.path, self.uuid, self.status, self.params
        )
