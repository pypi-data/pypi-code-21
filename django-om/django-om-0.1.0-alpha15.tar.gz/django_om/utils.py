from StringIO import StringIO
import decimal
import re

from transit.reader import Reader
from transit.writer import Writer
from transit.transit_types import Keyword, frozendict

from django_om import settings


def kebab_to_snake(match):
    return '{0}_{1}'.format(match.group()[0], match.group()[2])


def snake_to_kebab(match):
    return '{0}-{1}'.format(match.group()[0], match.group()[2])


def snakify(data):
    if isinstance(data, frozendict):
        new_dict = {}
        for key, value in data.items():
            key = str(key)  # Convert from transit_types.Keyword
            new_key = re.sub(r'[a-z]-[a-z]', kebab_to_snake, key)
            new_dict[new_key] = snakify(value)
        return new_dict
    if isinstance(data, (list, tuple)):
        data = list(data)
        for i in range(len(data)):
            try:
                data[i] = snakify(data[i])
            except:
                raise Exception(data)
        return data
    if isinstance(data, Keyword):
        data = re.sub(r'[a-z]-[a-z]', kebab_to_snake, str(data))
    return data


def kebabify(data):
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            if isinstance(key, str):
                key = re.sub(r"[A-Za-z0-9]_[A-Za-z0-9]", snake_to_kebab, key)
                key = Keyword(key)
            new_dict[key] = kebabify(value)
        return new_dict
    if isinstance(data, (list, tuple)):
        data = list(data)
        for i in range(len(data)):
            data[i] = kebabify(data[i])
        return data
    if isinstance(data, decimal.Decimal):
        return float(data)
    return data


def read_transit(transit_data):
    reader = Reader(settings.ENCODING)
    data = reader.read(StringIO(transit_data))
    data = snakify(data)
    return data


def write_transit(data):
    io = StringIO()
    writer = Writer(io, settings.ENCODING)
    data = kebabify(data)
    writer.write(data)
    transit_data = io.getvalue()
    return transit_data
