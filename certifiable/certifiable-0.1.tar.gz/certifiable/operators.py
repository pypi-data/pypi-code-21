#!/usr/bin/env python
# -*- coding: latin-1 -*-
#

from .errors import CertifierError, CertifierValueError

__all__ = [
    'ANY',
    'AND',
    'ALL',
    'NAND',
    'XOR',
    'certify_only_one',
    'certify_all',
    'certify_none',
    'certify_any',
]


def ANY(*args):
    """
    Don't care which callable args raise Certifier exceptions.

    :params iterable[Certifier] args:
        The certifiers to call
    """
    for arg in args:
        try:
            arg()
        except CertifierError:
            pass


def AND(*args, **kwargs):
    """
    ALL args must not raise an exception when called incrementally.
    If an exception is specified, raise it, otherwise raise the callable's exception.


    :params iterable[Certifier] args:
        The certifiers to call
    :param callable kwargs['exc']:
        Callable that excepts the unexpectedly raised exception as argument and return an
        exception to raise.
    :raises CertifierError:
        The first certifier error if at least one raises a certifier error.
    """
    for arg in args:
        try:
            arg()
        except CertifierError as e:
            exc = kwargs.get('exc', None)
            if exc is not None:
                raise exc(e)
            raise


def NAND(*args, **kwargs):
    """
    ALL args must raise an exception when called overall.
    Raise the specified exception on failure OR the first exception.

    :params iterable[Certifier] args:
        The certifiers to call
    :param callable kwargs['exc']:
        Callable that excepts the unexpectedly raised exception as argument and return an
        exception to raise.
    """
    errors = []

    for index, arg in enumerate(args):
        try:
            arg()
        except CertifierError as e:
            errors.append(e)

    if (len(errors) != len(args)) and len(args) > 1:
        exc = kwargs.get(
            'exc',
            CertifierValueError('Expecting no certified values'),
        )
        if exc is not None:
            raise exc


def XOR(a, b, exc=CertifierValueError('Expected at least one certified value')):
    """
    Only one arg must not raise a Certifier exception when called overall.
    Raise the specified exception on failure.

    :params Certifier a:
        The first certifiers to call
    :params Certifier b:
        The second certifiers to call
    :param Exception exc:
        Callable that is raised if XOR fails.
    """
    errors = []

    for certifier in [a, b]:
        try:
            certifier()
        except CertifierError as e:
            errors.append(e)

    if len(errors) != 1:
        if exc is not None:
            raise exc


ALL = AND
certify_only_one = XOR
certify_all = AND
certify_none = NAND
certify_any = ANY
