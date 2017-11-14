#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
from kser.entry import Entrypoint


class Task(Entrypoint):
    """"""
    def __init__(self, uuid=None, params=None, status="PENDING", **kwargs):
        Entrypoint.__init__(self, uuid=uuid, params=params, result=None)
        self.status = status
        self.metadata = kwargs

    def get_attr(self, item):
        attr = "{}Id".format(item)
        return attr, getattr(getattr(self, item, self), attr, None)

    def __repr__(self):
        return "Task [{}](uuid={},status={}, params={})".format(
            self.__class__.path, self.uuid, self.status, self.params
        )
