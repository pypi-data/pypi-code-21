#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
import os
import threading

import six

from .errors import CertifierError, CertifierParamError, CertifierTypeError, CertifierValueError

__all__ = [
    'make_certifier',
    'certify_required',
    'is_enabled',
    'enable',
    'disable',
    'enable_from_env',
    '_certify_int_param',
]

_undefined = object()

_local = threading.local()

ENVVAR = 'CERTIFIABLE_STATE'
DEFAULT_STATE = True


def exec_func(fn, val, **kwargs):
    return fn(val, **kwargs)


def make_certifier():
    """
    Decorator that can wrap raw functions to create a certifier function.

    Certifier functions support partial application.  If a function wrapped by
    `make_certifier` is called with a value as its first argument it will be
    certified immediately.  If no value is passed, then it will return a
    function that can be called at a later time.

    Assuming that `certify_something` has been decorated by `make_certifier`:
        >>> certify_something(value, foo=1, bar=2)

    Is equivalent to:
        >>> certifier = certify_something(foo=1, bar=2)
        >>> certifier(value)
    """

    def decorator(func):
        @six.wraps(func)
        def wrapper(value=_undefined, **kwargs):
            def certify(val):
                if is_enabled():
                    exec_func(func, val, **kwargs)

            if value is not _undefined:
                certify(value)
            else:
                return certify

        return wrapper

    return decorator


def certify_required(value, required=False):
    """
    Certify that a value is present if required.

    :param object value:
        The value that is to be certified.
    :param bool required:
        Is the value required?
    :raises CertifierValueError:
        Required value is `None`.

    """
    # Certify our kwargs:
    if not isinstance(required, bool):
        raise CertifierParamError(
            'required',
            required,
        )
    if value is None:
        if required:
            raise CertifierValueError(
                message="required value is None",
            )


def _certify_int_param(value, negative=True, required=False):
    """
    A private certifier (to `certifiable`) to certify integers from `certify_int`.

    :param int value:
        The value to certify is an integer.
    :param bool negative:
        If the value can be negative. Default=False.
    :param bool required:
        If the value is required. Default=False.
     :raises CertifierParamError:
        Value was not an integer (if required and non-None).
   """
    if value is None and not required:
        return

    if not isinstance(value, int):
        raise CertifierTypeError(
            message="expected integer, but value is of type {cls!r}".format(
                cls=value.__class__.__name__),
            value=value,
            required=required,

        )
    if not negative and value < 0:
        raise CertifierValueError(
            message="expected positive integer, but value is negative")


def certify_parameter(certifier, name, value, kwargs=None):
    """
    Internal certifier for kwargs passed to Certifiable public methods.

    :param callable certifier:
        The certifier to use
    :param str name:
        The name of the kwargs
    :param object value:
        The value of the kwarg.
    :param bool required:
        Is the param required. Default=False.
    :raises CertifierParamError:
        A parameter failed internal certification.
    """
    try:
        certifier(value, **kwargs or {})
    except CertifierError as err:
        six.raise_from(
            CertifierParamError(
                name,
                value,
            ),
            err)


def certify_params(*many_params):
    for params in many_params:
        certify_parameter(*params)


def _enabler(state):
    _local.state = bool(state)
    return _local.state


def is_enabled():
    """
    Determine if certification is enabled for this thread.

    :return:
        The current enabled state.
    :rtype:
        bool
    """
    return _local.state


def enable(enabler=True):
    """
    Disable certification for this thread.

    :return:
        The new state.
    :rtype:
        bool
    """
    return _enabler(
        bool(enabler))


def disable():
    """
    Disable certification for this thread.

    :return:
        The new state.
    :rtype:
        bool
    """
    return _enabler(False)


def enable_from_env(state=None):
    """
    Enable certification for this thread based on the environment variable `CERTIFIABLE_STATE`.

    :param bool state:
        Default status to use.
    :return:
        The new state.
    :rtype:
        bool
    """
    try:
        x = os.environ.get(
            ENVVAR,
            state,
        )
        value = bool(int(x))
    except Exception:
        value = bool(state)

    return enable(value)


_local.state = DEFAULT_STATE
