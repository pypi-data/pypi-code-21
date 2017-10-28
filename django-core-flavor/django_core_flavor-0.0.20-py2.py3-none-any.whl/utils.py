import re

from importlib import import_module

import elastic_sdk

from django.apps import apps
from django.conf import settings


def get_elastic_client(doc_prefix=None):
    return elastic_sdk.Client(
        index_name=settings.ELASTIC_INDEX,
        doc_prefix=doc_prefix,
        hostnames=settings.ELASTIC_HOSTNAMES)


def camel_to_dashed(camel_data,
                    first_capital_regex=re.compile('(.)([A-Z][a-z]+)'),
                    all_capital_regex=re.compile('([a-z0-9])([A-Z])')):

    data = {}
    for key, value in camel_data.items():
        if isinstance(value, dict):
            value = camel_to_dashed(value)

        s1 = first_capital_regex.sub(r'\1_\2', key)
        data[all_capital_regex.sub(r'\1_\2', s1).lower()] = value
    return data


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def sizeof_fmt(num):
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')


def round_decimals(value, decimals=2):
    return int(round(value * 10 ** decimals))


def import_from_string(value):
    try:
        parts = value.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as err:
        msg = "Could not import '{}'. {}: {}."\
            .format(value, err.__class__.__name__, err)
        raise ImportError(msg)


def get_model(value):
    parts = value.split('.')
    return apps.get_model(app_label=parts[0], model_name=parts[-1])
