#!/usr/bin/env python
# -*- coding: latin-1 -*-
#

import string
from datetime import date, datetime, time
from decimal import Decimal

import six

from .errors import CertifierTypeError, CertifierValueError
from .utils import _certify_int_param, certify_params, certify_required, make_certifier

__all__ = [
    'certify_printable',
    'certify_text',
    'certify_int',
    'certify_number',
    'certify_bool',
    'certify_bytes',
    'certify_enum',
    'certify_enum_value',
    'certify_object',
    'certify_timestamp',
    'certify_date',
    'certify_time',
]


def _certify_printable(value, nonprintable=False, required=True):
    if value is None and not required:
        return
    if not nonprintable and any(char not in string.printable for char in value):
        raise CertifierValueError(
            message="string contains non-printable characters",
            value=value,
            required=required,
        )


@make_certifier()
def certify_printable(value, nonprintable=False, required=True):
    """
    Certifier for human readable (printable) values.

    :param unicode value:
        The string to be certified.
    :param nonprintable:
        Whether the string can contain non-printable characters. Non-printable characters are
        allowed by default.
    :param bool required:
        Whether the value can be `None`. Defaults to True.
    :raises CertifierTypeError:
        The type is invalid
    :raises CertifierValueError:
        The value is invalid
    """
    certify_params(
        (certify_bool, 'nonprintable', nonprintable),
    )
    certify_required(
        value=value,
        required=required,
    )
    if value is None and not required:
        return
    _certify_printable(
        value=value,
        nonprintable=nonprintable,
        required=required,
    )


@make_certifier()
def certify_text(
    value, min_length=None, max_length=None, nonprintable=True, required=True,
):
    """
    Certifier for human readable string values.

    :param unicode value:
        The string to be certified.
    :param int min_length:
        The minimum length of the string.
    :param int max_length:
        The maximum acceptable length for the string. By default, the length is not checked.
    :param nonprintable:
        Whether the string can contain non-printable characters. Non-printable characters are
        allowed by default.
    :param bool required:
        Whether the value can be `None`. Defaults to True.
    :raises CertifierTypeError:
        The type is invalid
    :raises CertifierValueError:
        The value is invalid
    """
    certify_params(
        (_certify_int_param, 'max_length', max_length, dict(negative=False, required=False)),
        (_certify_int_param, 'min_length', min_length, dict(negative=False, required=False)),
        (certify_bool, 'nonprintable', nonprintable),
    )
    certify_required(
        value=value,
        required=required,
    )
    if value is None and not required:
        return

    if not isinstance(value, six.text_type):
        raise CertifierTypeError(
            message="expected unicode string, but value is of type {cls!r}".format(
                cls=value.__class__.__name__),
            value=value,
            required=required,
        )

    if min_length is not None and len(value) < min_length:
        raise CertifierValueError(
            message="{length} is shorter than minimum acceptable {min}".format(
                length=len(value), min=min_length),
            value=value,
            required=required,
        )

    if max_length is not None and len(value) > max_length:
        raise CertifierValueError(
            message="{length} is longer than maximum acceptable {max}".format(
                length=len(value), max=max_length),
            value=value,
            required=required,
        )

    _certify_printable(
        value=value,
        nonprintable=nonprintable,
        required=required,
    )


@make_certifier()
def certify_string(
    value, min_length=None, max_length=None, nonprintable=True, required=True,
):
    """
    Certifier for human readable string values.

    :param unicode value:
        The string to be certified.
    :param int min_length:
        The minimum length of the string.
    :param int max_length:
        The maximum acceptable length for the string. By default, the length is not checked.
    :param nonprintable:
        Whether the string can contain non-printable characters. Non-printable characters are
        allowed by default.
    :param bool required:
        Whether the value can be `None`. Defaults to True.
    :raises CertifierTypeError:
        The type is invalid
    :raises CertifierValueError:
        The value is invalid
    """
    certify_params(
        (_certify_int_param, 'max_length', max_length, dict(negative=False, required=False)),
        (_certify_int_param, 'min_length', min_length, dict(negative=False, required=False)),
        (certify_int, 'nonprintable', nonprintable),
    )
    certify_required(
        value=value,
        required=required,
    )
    if value is None and not required:
        return

    if not isinstance(value, six.string_types):
        raise CertifierTypeError(
            message="expected string, but value is of type {cls!r}".format(
                cls=value.__class__.__name__),
            value=value,
            required=required,
        )

    if min_length is not None and len(value) < min_length:
        raise CertifierValueError(
            message="{length} is shorter than minimum acceptable {min}".format(
                length=len(value), min=min_length),
            value=value,
            required=required,
        )

    if max_length is not None and len(value) > max_length:
        raise CertifierValueError(
            message="{length} is longer than maximum acceptable {max}".format(
                length=len(value), max=max_length),
            value=value,
            required=required,
        )

    _certify_printable(
        value=value,
        nonprintable=nonprintable,
        required=required,
    )


@make_certifier()
def certify_int(value, min_value=None, max_value=None, required=True):
    """
    Certifier for integer values.

    :param six.integer_types value:
        The number to be certified.
    :param int min_value:
        The minimum acceptable value for the number.
    :param int max_value:
        The maximum acceptable value for the number.
    :param bool required:
        Whether the value can be `None`. Defaults to True.
    :raises CertifierTypeError:
        The type is invalid
    :raises CertifierValueError:
        The value is invalid
    """
    certify_params(
        (_certify_int_param, 'max_length', max_value, dict(negative=True, required=False)),
        (_certify_int_param, 'min_length', min_value, dict(negative=True, required=False)),
    )
    certify_required(
        value=value,
        required=required,
    )
    if value is None and not required:
        return

    if not isinstance(value, six.integer_types):
        raise CertifierTypeError(
            message="expected integer, but value is of type {cls!r}".format(
                cls=value.__class__.__name__),
            value=value,
            required=required,
        )

    if min_value is not None and value < min_value:
        raise CertifierValueError(
            message="{value} is less than minimum acceptable {min}".format(
                value=value, min=min_value),
            value=value,
            required=required,
        )

    if max_value is not None and value > max_value:
        raise CertifierValueError(
            message="{value} is more than minimum acceptable {max}".format(
                value=value, max=max_value),
            value=value,
            required=required,
        )


@make_certifier()
def certify_number(value, min_value=None, max_value=None, required=True):
    """
    Certifier for numeral values.

    :param six.integer_types|float value:
        The number to be certified.
    :param int min_value:
        The minimum acceptable value for the number.
    :param int max_value:
        The maximum acceptable value for the number.
    :param bool required:
        Whether the value can be `None`.  Defaults to True.
    :raises CertifierTypeError:
        The type is invalid
    :raises CertifierValueError:
        The value is invalid
    """
    certify_params(
        (_certify_int_param, 'max_value', max_value, dict(negative=True, required=False)),
        (_certify_int_param, 'max_value', max_value, dict(negative=True, required=False)),
    )
    certify_required(
        value=value,
        required=required,
    )
    if value is None and not required:
        return

    if not isinstance(value, six.integer_types + (float, Decimal)):
        raise CertifierTypeError(
            message="expected integer or float, but value is of type {cls!r}".format(
                cls=value.__class__.__name__),
            value=value,
            required=required,
        )

    if min_value is not None and value < min_value:
        raise CertifierValueError(
            message="{value} is less than minimum acceptable {min}".format(
                value=value, min=min_value),
            value=value,
            required=required,
        )

    if max_value is not None and value > max_value:
        raise CertifierValueError(
            message="{value} is more than minimum acceptable {max}".format(
                value=value, max=max_value),
            value=value,
            required=required,
        )


@make_certifier()
def certify_bool(value, required=True):
    """
    Certifier for boolean values.

    :param value:
        The value to be certified.
    :param bool required:
        Whether the value can be `None`.  Defaults to True.
    :raises CertifierTypeError:
        The type is invalid
    """
    certify_required(
        value=value,
        required=required,
    )
    if value is None and not required:
        return

    if not isinstance(value, bool):
        raise CertifierTypeError(
            message="expected bool, but value is of type {cls!r}".format(
                cls=value.__class__.__name__),
            value=value,
            required=required,
        )


@make_certifier()
def certify_bytes(value, min_length=None, max_length=None, required=True):
    """
    Certifier for bytestring values.

    Should not be used for certifying human readable strings, Please use `certify_string` instead.

    :param bytes|str value:
        The string to be certified.
    :param int min_length:
        The minimum length of the string.
    :param int max_length:
        The maximum acceptable length for the string. By default, the length is
        not checked.
    :param bool required:
        Whether the value can be `None`. Defaults to True.
    :raises CertifierTypeError:
        The type is invalid
    :raises CertifierValueError:
        The value is invalid
    """
    certify_params(
        (_certify_int_param, 'min_value', min_length, dict(negative=False, required=False)),
        (_certify_int_param, 'max_value', max_length, dict(negative=False, required=False)),
    )

    certify_required(
        value=value,
        required=required,
    )
    if value is None and not required:
        return

    if not isinstance(value, six.binary_type):
        raise CertifierTypeError(
            message="expected byte string, but value is of type {cls!r}".format(
                cls=value.__class__.__name__),
            value=value,
            required=required,
        )

    if min_length is not None and len(value) < min_length:
        raise CertifierValueError(
            message="{length} is shorter than minimum acceptable {min}".format(
                length=len(value), min=min_length),
            value=value,
            required=required,
        )

    if max_length is not None and len(value) > max_length:
        raise CertifierValueError(
            message="{length} is longer than maximum acceptable {max}".format(
                length=len(value), max=max_length),
            value=value,
            required=required,
        )


@make_certifier()
def certify_enum(value, kind=None, required=True):
    """
    Certifier for enum.

    :param value:
        The value to be certified.
    :param kind:
        The enum type that value should be an instance of.
    :param bool required:
        Whether the value can be `None`. Defaults to True.
    :raises CertifierTypeError:
        The type is invalid
    """
    certify_required(
        value=value,
        required=required,
    )
    if value is None and not required:
        return

    if not isinstance(value, kind):
        raise CertifierTypeError(
            message="expected {expected!r}, but value is of type {actual!r}".format(
                expected=kind.__name__, actual=value.__class__.__name__),
            value=value,
            required=required,
        )


@make_certifier()
def certify_enum_value(value, kind=None, required=True):
    """
    Certifier for enum values.

    :param value:
        The value to be certified.
    :param kind:
        The enum type that value should be an instance of.
    :param bool required:
        Whether the value can be `None`. Defaults to True.
    :raises CertifierValueError:
        The type is invalid
    """
    certify_required(
        value=value,
        required=required,
    )
    if value is None and not required:
        return

    try:
        kind(value)
    except:
        raise CertifierValueError(
            message="value {value!r} is not a valid member of {enum!r}".format(
                value=value, enum=kind.__name__),
            value=value,
            required=required,
        )


@make_certifier()
def certify_object(value, kind=None, required=True):
    """
    Certifier for class object.

    :param object value:
        The object to certify.
    :param object kind:
        The type of the model that the value is expected to evaluate to.
    :param bool required:
        Whether the value can be `None`. Defaults to True.
    :raises CertifierTypeError:
        The type is invalid
    :raises CertifierValueError:
        The value is invalid
    """
    certify_required(
        value=value,
        required=required,
    )
    if value is None and not required:
        return

    if not isinstance(value, kind):
        try:
            name = value.__class__.__name__
        except:  # noqa # pragma: no cover
            name = type(value).__name__

        try:
            expected = kind.__class__.__name__
        except:  # noqa # pragma: no cover
            expected = type(kind).__name__

        raise CertifierValueError(
            message="Expected object {expected!r}, but got {actual!r}".format(
                expected=expected, actual=name),
            value=value,
            required=required,
        )


@make_certifier()
def certify_timestamp(value, required=True):
    """
    Certifier for timestamp (datetime) values.

    :param value:
        The value to be certified.
    :param bool required:
        Whether the value can be `None`. Defaults to True.
    :raises CertifierTypeError:
        The type is invalid
    """
    certify_required(
        value=value,
        required=required,
    )
    if value is None and not required:
        return

    if not isinstance(value, datetime):
        raise CertifierTypeError(
            message="expected timestamp (datetime), but value is of type {cls!r}".format(
                cls=value.__class__.__name__),
            value=value,
            required=required,
        )


@make_certifier()
def certify_date(value, required=True):
    """
    Certifier for datetime.date values.

    :param value:
        The value to be certified.
    :param bool required:
        Whether the value can be `None`  Defaults to True.
    :raises CertifierTypeError:
        The type is invalid
    """
    certify_required(
        value=value,
        required=required,
    )
    if value is None and not required:
        return

    if not isinstance(value, date):
        raise CertifierTypeError(
            message="expected timestamp (date∂), but value is of type {cls!r}".format(
                cls=value.__class__.__name__),
            value=value,
            required=required,
        )


@make_certifier()
def certify_time(value, required=True):
    """
    Certifier for datetime.time values.

    :param value:
        The value to be certified.
    :param bool required:
        Whether the value can be `None`  Defaults to True.
    :raises CertifierTypeError:
        The type is invalid
    """
    certify_required(
        value=value,
        required=required,
    )
    if value is None and not required:
        return

    if not isinstance(value, time):
        raise CertifierTypeError(
            message="expected timestamp (time), but value is of type {cls!r}".format(
                cls=value.__class__.__name__),
            value=value,
            required=required,
        )
