#!/usr/bin/python
# -*- coding: utf-8 -*-

import json

import appier

class BDCommon(object):

    @classmethod
    def get_l(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    @classmethod
    def bd_id_e(cls, value, default = None):
        return cls._bd_type_e(
            value,
            int,
            default = default
        )

    @classmethod
    def bd_unicode_e(cls, value, default = None):
        return cls._bd_type_e(
            value,
            appier.legacy.UNICODE,
            default = default
        )

    @classmethod
    def bd_json_e(cls, value, sort_keys = False, default = None):
        if value == None: return default
        return json.dumps(value, sort_keys = sort_keys)

    @classmethod
    def bd_unicode_d(cls, model, attribute, default = None):
        return cls._bd_type_d(
            model,
            attribute,
            appier.legacy.UNICODE,
            default = default
        )

    @classmethod
    def bd_json_d(cls, model, attribute, default = None):
        value = cls.bd_value_d(model, attribute)
        if value == None: return default
        return json.loads(value)

    @classmethod
    def bd_value_d(cls, model, attribute, default = None):
        attributes = attribute.split(".")
        _model = model
        for attribute in attributes:
            _model = _model.get(attribute, None)
            if _model == None: break
        value = _model
        if value == None: value = default
        return value

    @classmethod
    def _bd_type_e(cls, value, type, default = None):
        if value == None: return default
        value = type(value)
        return value

    @classmethod
    def _bd_type_d(cls, model, attribute, type, default = None):
        value = cls.bd_value_d(model, attribute)
        if value == None: return default
        value = type(value)
        return value

def handle_error(function, fallback = None, code = 400, encoding = "utf-8"):
    def decorator(*args, **kwargs):
        try: return function(*args, **kwargs)
        except appier.HTTPError as error:
            _handle_error(
                error,
                fallback = fallback,
                code = code,
                encoding = encoding
            )

    return decorator

def _handle_error(error, fallback = None, code = 400, encoding = "utf-8"):
    # reads the complete set of data from the error (assumes
    # that the error is string based and implements a read interface)
    data = error.read()

    # tries to retrieve the proper message by decoding the
    # received bytes using the provided encoding value, in
    # case it fails sets a default message (as fallback)
    is_bytes = appier.legacy.is_bytes(data)
    try: data_s = data.decode(encoding) if is_bytes else str(data)
    except UnicodeDecodeError: data_s = "Undefined message"

    try:
        # tries to load the data as a json based message (for
        # structure parsing) may fail due to bad json structure
        # if the message data is not json valid
        data_j = json.loads(data_s)

        # tries to retrieve the message from the provided
        # information, as expected by the structure
        message = data_j.get("message", None)
    except:
        # in case there was an unexpected error interpreting
        # the data then sets the data itself as the message
        message = data_s

    # in case the message is defined special final characters
    # must be removed in order to normalize the message
    if message: message = message.rstrip(".")

    # in case there is no message then uses the fallback instead
    # as the fallback should represent the same error but in a
    # much broader sense (less accurate)
    fallback = fallback or data_s
    message = message or fallback

    # raises the error as an exception using the proper internal
    # usage error format (as expected by upper layers)
    raise appier.OperationalError(
        message = message,
        code = code
    )
