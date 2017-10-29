#!/usr/bin/env python
# -*- coding: latin-1 -*-
#

__all__ = [
    'CertifierError',
    'CertifierValueError',
    'CertifierTypeError',
]


class CertifierErrorBase(Exception):
    """
    Base class of all certifier exceptions.
    """


class CertifierError(CertifierErrorBase):
    """
    Base class of all checked certifier exceptions.
    """

    def __init__(self, message, value=None, required=None):
        super(CertifierError, self).__init__(message)
        self.value = value
        self.required = required


class CertifierRuntimeError(CertifierErrorBase):
    """
    Base class of all exceptions raised as a result of bad params pass
    to certifier kwargs.
    """

    def __init__(self, desc):
        msg = 'Certifier internal error - {desc}'.format(
            desc=desc,
        )
        super(CertifierRuntimeError, self).__init__(msg)


class CertifierValueError(CertifierError, ValueError):
    pass


class CertifierTypeError(CertifierError, TypeError):
    pass


class CertifierParamError(CertifierRuntimeError):
    def __init__(self, name=None, value=None):
        msg = 'Bad param passed to certifier: name: {name}, value: {value}'.format(
            name=name,
            value=value,
        )
        super(CertifierParamError, self).__init__(msg)
        self.name = name
        self.value = value
