#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import traceback
from uuid import uuid4
from marshmallow import Schema, fields

from cdumay_rest_client.exceptions import HTTPException, HTTPExceptionValidator


def random_uuid():
    """description of random_uuid"""
    return str(uuid4())


class ResultSchema(Schema):
    uuid = fields.String()
    retcode = fields.Integer(default=0)
    stdout = fields.String(default="")
    stderr = fields.String(default="")
    retval = fields.Dict()


class Result(object):
    def __init__(self, retcode=0, stdout="", stderr="", retval=None, uuid=None):
        self.retcode = retcode
        self.stdout = stdout
        self.stderr = stderr
        self.retval = retval or dict()
        self.uuid = uuid if uuid else random_uuid()

    def print(self, data):
        """Store text in result's stdout

        :param Any data: Any printable data
        """
        self.stdout += "{}\n".format(data)

    def print_err(self, data):
        """Store text in result's stderr

        :param Any data: Any printable data
        """
        self.stderr += "{}\n".format(data)

    @staticmethod
    def fromException(exc, uuid=None):
        """ Serialize an exception into a result

        :param Exception exc: Exception raised
        :param str uuid: Current Kafka :class:`kser.transport.Message` uuid
        :rtype: :class:`kser.result.Result`
        """
        if not isinstance(exc, HTTPException):
            exc = HTTPException(code=500, message=str(exc))

        return Result(
            uuid=exc.extra.get("uuid", uuid or random_uuid()),
            retcode=exc.code, stderr=exc.message,
            retval=dict(error=HTTPExceptionValidator().dump(exc).data)
        )

    def __add__(self, o):
        """description of __add__"""
        self.retcode = self.retcode if self.retcode > o.retcode else o.retcode
        self.retval.update(o.retval)
        self.stdout += "\n{}".format(o.stdout) if len(o.stdout) > 0 else ""
        self.stderr += "\n{}".format(o.stderr) if len(o.stderr) > 0 else ""
        return self

    def __str__(self):
        return self.stdout if self.retcode == 0 else self.stderr

    def __repr__(self):
        """"""
        return "Result<retcode='{}'>".format(self.retcode)
