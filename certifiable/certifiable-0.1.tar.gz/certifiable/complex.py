#!/usr/bin/env python
# -*- coding: latin-1 -*-

from collections import Mapping, MutableMapping, MutableSequence, MutableSet, Sequence, Set
from types import DictType

import email_validator
import six

from .core import certify_bool, certify_int, certify_text
from .errors import CertifierError, CertifierParamError, CertifierTypeError, CertifierValueError
from .utils import _certify_int_param, certify_params, certify_required, make_certifier

__all__ = [
    'certify_dict',
    'certify_set',
    'certify_tuple',
    'certify_list',
    'certify_email',
    'certify_dict_schema',
    'certify_iterable_schema',
]


def certify_dict_schema(
    value, schema, key_certifier=None, value_certifier=None, required=None, allow_extra=None,
):
    if key_certifier is not None or value_certifier is not None:
        for key, value in value.items():
            if key_certifier is not None:
                key_certifier(key)
            if value_certifier is not None:
                value_certifier(key)

    if schema:
        if not isinstance(schema, DictType):
            raise CertifierParamError(
                name='schema',
                value=schema,
            )

        for key, certifier in schema.items():
            if key not in value:
                raise CertifierValueError(
                    message="key \'{key}\' missing from dictionary".format(
                        key=key),
                    required=required,
                )
            val = value[key]
            certifier(value=val)

        if not allow_extra and set(schema) != set(value):
            values = set(value) - set(schema)
            raise CertifierValueError(
                message="encountered unexpected keys: {unexpected!r}".format(
                    unexpected=values),
                value=values,
                required=required,
            )


@make_certifier()
def certify_dict(
    value, schema=None, allow_extra=False, required=True, key_certifier=None, value_certifier=None,
    include_collections=False,
):
    """
    Certifies a dictionary, checking it against an optional schema.

    The schema should be a dictionary, with keys corresponding to the expected keys in `value`,
    but with the values replaced by functions which will be called to with the corresponding
    value in the input.

    A simple example:

        >>> certifier = certify_dict(schema={
        ...    'id': certify_key(kind='Model'),
        ...    'count': certify_int(min=0),
        ...    })
        >>> certifier({'id': self.key, 'count': self.count})

    :param dict value:
        The value to be certified.
    :param dict schema:
        The schema against which the value should be checked.
    :param bool allow_extra:
        Set to `True` to ignore extra keys.
    :param bool required:
        Whether the value can't be `None`. Defaults to True.
    :param callable key_certifier:
        callable that receives the key to certify (ignoring schema keys).
    :param callable value_certifier:
        callable that receives the value to certify (ignoring schema values).
    :param bool include_collections:
        Include types from collections.
    :raises CertifierTypeError:
        The type is invalid
    :raises CertifierValueError:
        The value is invalid
    """
    cls = DictType

    # Certify our kwargs:
    certify_params(
        (certify_bool, 'allow_extra', allow_extra),
        (certify_bool, 'include_collections', include_collections),
    )
    certify_required(
        value=value,
        required=required,
    )

    # Check the type(s):
    types = [cls]
    if include_collections:
        types.extend([Mapping, MutableMapping])
    types = tuple(types)
    if not isinstance(value, types):
        raise CertifierTypeError(
            message="Expected {t} but the type is {cls!r}".format(
                cls=cls,
                t=value.__class__.__name__,
                value=value,
                required=required,
            ))
    certify_dict_schema(
        value=value,
        schema=schema,
        key_certifier=key_certifier,
        value_certifier=value_certifier,
        required=required,
        allow_extra=allow_extra,
    )


def certify_iterable_schema(value, schema, required):
    if schema is not None:
        if len(schema) != len(value):
            raise CertifierValueError(
                "encountered {extra} extra items".format(
                    extra=len(value) - len(schema)),
                value=value,
                required=required,
            )

        for index, certifier in enumerate(schema):
            try:
                certifier(value=value[index])
            except CertifierError as exc:
                six.raise_from(
                    CertifierValueError(
                        message="invalid value {value!r} for item {index}".format(
                            index=index, value=value[index]),
                        value=value,
                        required=required,
                    ),
                    exc,
                )


def _certify_iterable(
    cls, extra_cls, value=None, certifier=None, min_len=None, max_len=None, schema=None,
    required=True
):
    """
    Validates an iterable sequence, checking it against an optional schema.

    The schema should be a list of expected values replaced by functions which will be called to
    with the corresponding value in the input.

    :param iterable value:
        The value to be certified.
    :param func\None certifier:
        A function to be called on each value in the iterable to check that it is valid.
    :param int\None min_len:
        The minimum acceptable length for the iterable.  If None, the minimum length is not checked.
    :param int\None max_len:
        The maximum acceptable length for the iterable.  If None, the maximum length is not checked.
    :param tuple\None schema:
        The schema against which the value should be checked.
        For single-item tuple make sure to add comma at the end of schema tuple, that is,
        for example: schema=(certify_int(),)
    :param bool required:
        Whether the value can't be `None`. Defaults to True.
    :raises CertifierTypeError:
        The type is invalid
    :raises CertifierValueError:
        The valid is invalid
    """
    certify_required(
        value=value,
        required=required,
    )
    certify_params(
        (_certify_int_param, 'max_len', max_len, dict(negative=False, required=False)),
        (_certify_int_param, 'min_len', min_len, dict(negative=False, required=False)),
    )
    # Check the type(s):
    types = [cls]
    if extra_cls:
        types.extend(extra_cls)
    types = tuple(types)
    if not isinstance(value, types):
        raise CertifierTypeError(
            message="value is not a tuple ({value_type!r})".format(
                value_type=value.__class__.__name__
            ),
            value=value,
            required=required,
        )
    if min_len is not None and len(value) < min_len:
        raise CertifierValueError(
            message="expected at least {expected} elements, "
                    "but set is of length {actual}".format(expected=min_len, actual=len(value)),
            value=value,
            required=required,
        )

    if max_len is not None and len(value) > max_len:
        raise CertifierValueError(
            message=("expected at most {expected} elements, "
                     "but {cls} is of length {actual}").format(
                expected=max_len,
                actual=len(value),
                cls=cls.__name__,
            ),
            value=value,
            required=required,
        )
    # Apply the certifier to all values:
    if certifier is not None:
        map(certifier, value)
    certify_iterable_schema(
        value=value,
        schema=schema,
        required=required,
    )


@make_certifier()
def certify_set(
    value, certifier=None, min_len=None, max_len=None, include_collections=False,
    required=True,
):
    """
    Certifier for a set.

    :param set value:
        The set to be certified.
    :param func certifier:
        A function to be called on each value in the list to check that it is valid.
    :param int min_len:
        The minimum acceptable length for the list. If None, the minimum length is not checked.
    :param int max_len:
        The maximum acceptable length for the list. If None, the maximum length is not checked.
    :param bool include_collections:
        Include types from collections.
    :param bool required:
        Whether the value can be `None`. Defaults to True.
    :raises CertifierTypeError:
        The type is invalid
    :raises CertifierValueError:
        The valid is invalid
    """
    certify_bool(include_collections, required=True)
    return _certify_iterable(
        set,
        tuple([MutableSet, Set]) if include_collections else tuple(),
        value=value,
        certifier=certifier,
        min_len=min_len,
        max_len=max_len,
        schema=None,
        required=required,
    )


@make_certifier()
def certify_tuple(value, certifier=None, min_len=None, max_len=None, required=True, schema=None):
    """
    Validates a tuple, checking it against an optional schema.

    The schema should be a list of expected values replaced by functions which will be called to
    with the corresponding value in the input.

    A simple example:

        >>> certifier = certify_tuple(schema=(
        ...     certify_key(kind='Model'),
        ...     certify_int(min=0),
        ...     ))
        >>> certifier((self.key, self.count))

    :param tuple value:
        The value to be certified.
    :param func certifier:
        A function to be called on each value in the iterable to check that it is valid.
    :param int min_len:
        The minimum acceptable length for the iterable.  If None, the minimum length is not checked.
    :param int max_len:
        The maximum acceptable length for the iterable.  If None, the maximum length is not checked.
    :param bool required:
        Whether the value can't be `None`. Defaults to True.
    :param tuple schema:
        The schema against which the value should be checked.
        For single-item tuple make sure to add comma at the end of schema tuple, that is,
        for example: schema=(certify_int(),)
    :raises CertifierTypeError:
        The type is invalid
    :raises CertifierValueError:
        The valid is invalid
    """
    return _certify_iterable(
        tuple,
        tuple(),
        value=value,
        certifier=certifier,
        min_len=min_len,
        max_len=max_len,
        schema=schema,
        required=required,
    )


@make_certifier()
def certify_list(
    value, certifier=None, min_len=None, max_len=None, required=True, schema=None,
    include_collections=False,
):
    """
    Certifier for a list.

    :param list value:
        The array to be certified.
    :param func certifier:
        A function to be called on each value in the iterable to check that it is valid.
    :param int min_len:
        The minimum acceptable length for the iterable.  If None, the minimum length is not checked.
    :param int max_len:
        The maximum acceptable length for the iterable.  If None, the maximum length is not checked.
    :param bool required:
        Whether the value can't be `None`. Defaults to True.
    :param tuple schema:
        The schema against which the value should be checked.
        For single-item tuple make sure to add comma at the end of schema tuple, that is,
        for example: schema=(certify_int(),)
    :param bool include_collections:
        Include types from collections.
    :raises CertifierTypeError:
        The type is invalid
    :raises CertifierValueError:
        The valid is invalid
    """
    certify_bool(include_collections, required=True)
    return _certify_iterable(
        list,
        tuple([MutableSequence, Sequence]) if include_collections else tuple(),
        value=value,
        certifier=certifier,
        min_len=min_len,
        max_len=max_len,
        schema=schema,
        required=required,
    )


@make_certifier()
def certify_email(value, required=True):
    """
    Certifier which verifies that email addresses are well-formed.

    Does not check that the address exists.

    :param unicode value:
        The email address to certify. **Should be normalized!**
    :param bool required:
        Whether the value can be `None`. Defaults to True.
    :raises CertifierTypeError:
        The type is invalid
    :raises CertifierValueError:
        The valid is invalid
    """
    certify_required(
        value=value,
        required=required,
    )

    certify_text(value, min_length=3, max_length=320)

    try:
        certification_result = email_validator.validate_email(
            value,
            check_deliverability=False,
        )
    except email_validator.EmailNotValidError as ex:
        six.raise_from(
            CertifierValueError(
                message="{value!r} is not a valid email address: {ex}".format(
                    value=value,
                    # email_validator returns unicode characters in exception string
                    ex=repr(unicode(ex))
                ),
                value=value,
                required=required,
            ),
            ex
        )
    else:
        if value != certification_result['email']:
            raise CertifierValueError(
                message="{value!r} is not normalized, should be {normalized!r}".format(
                    value=value, normalized=certification_result['email']),
                value=value,
                required=required,
            )
