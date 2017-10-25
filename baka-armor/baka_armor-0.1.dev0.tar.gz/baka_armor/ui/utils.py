""""
 # Copyright (c) 07 2016 | suryakencana
 # 7/12/16 nanang.ask@kubuskotak.com
 #  utils
"""
from datetime import datetime, date, time
from decimal import Decimal
from uuid import uuid4

from bitmath import Byte, MiB
from dateutil.parser import parse as pdt
from pytz import timezone
import sys

from babel.dates import (
    format_date as fd,
    format_datetime as fdt,
    format_time as ft,
    get_date_format as gdf,
    get_time_format as gtf,
    get_datetime_format as gdtf,
    parse_date as pd
)
from babel.numbers import (
    format_decimal as fdc,
    format_currency as fc
)
from pyramid.threadlocal import get_current_registry
import random


def get_settings():
    registry = get_current_registry()
    return registry.settings


def get_locale_name():
    settings = get_settings()
    return settings.get('company.locale_name', 'en')


def get_timezone():
    settings = get_settings()
    return settings.get('company.timezone', 'Asia/Jakarta')


def gen_id(prefix='', limit=6):
    s = list(str(int(uuid4())))
    random.shuffle(s)
    return u"%s%s" % (prefix, ''.join(s[:limit]))


def get_company_name():
    settings = get_settings()
    return settings.get('company.name', '')


def get_base_currency():
    settings = get_settings()
    return settings.get('company.base_currency', 'usd')


def get_date_format():
    return gdf(format='short', locale=get_locale_name()).pattern


def get_time_format():
    return gtf(format='short', locale=get_locale_name()).pattern


def get_datetime_format():
    f = gdtf(format='short', locale=get_locale_name())
    return f.format(get_time_format(), get_date_format())


def parse_datetime(s):
    return timezone(get_timezone()).localize(pdt(s))


def parse_date(s):
    return pd(s, locale=get_locale_name())


def format_date(value, _format=None):
    if not value:
        return ''
    return fd(
        value, format=(_format or get_date_format()), locale=get_locale_name()
    )


def format_datetime(value):
    return fdt(
        value, format=get_datetime_format(),
        locale=get_locale_name(), tzinfo=timezone(get_timezone())
    )


def format_time(value):
    return ft(
        value, format=get_time_format(), locale=get_locale_name()
    )


def format_decimal(value, quantize='.01'):
    value = Decimal(value).quantize(Decimal(quantize))
    return fdc(value, locale=get_locale_name())


def serialize(value):
    if isinstance(value, datetime):
        return format_datetime(value)
    if isinstance(value, date):
        return format_date(value)
    if isinstance(value, time):
        return format_time(value)
    if isinstance(value, Decimal):
        return format_decimal(value)
    if hasattr(value, 'serialize'):
        return value.serialize()
    return value


def format_currency(value, currency):
    return fc(value, currency, locale=get_locale_name())


def date_now(_format="%d.m.%Y %H:%M:%S"):
    """ returns the formated datetime """
    return datetime.now().strftime(_format)


def get_storage_dir():
    dt = datetime.now(tz=timezone(get_timezone()))
    return "%d%d%d" % (dt.year, dt.month, dt.day)


def get_storage_max_size():
    settings = get_settings()
    return settings.get('storage.max_size')

# storages
CHUNK_SIZE = 1024


def is_allowed_file_size(f):
    """ check if given file size is less or equal as max allowed in config
    """
    max_size = get_storage_max_size()
    return Byte(get_file_size(f)) <= MiB(float(max_size))


def get_file_size(f):
    """ get file size in Bytes
    """
    size = 0
    while True:
        chunk = f.read(CHUNK_SIZE)
        if not chunk:
            break
        size += sys.getsizeof(chunk)
    return size
