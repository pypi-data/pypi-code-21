# -*- coding: UTF-8 -*-
"""
    trytond_async_sqs.serialization

    Backports the 3.4 implementation of JSONEncoder and Decoder.
"""
import functools
import datetime
from decimal import Decimal
try:
    import simplejson as json
except ImportError:
    import json
import base64
from trytond.model import Model
from trytond.pool import Pool


class JSONDecoder(object):

    decoders = {}

    @classmethod
    def register(cls, klass, decoder):
        assert klass not in cls.decoders
        cls.decoders[klass] = decoder

    def __call__(self, dct):
        if dct.get('__class__') in self.decoders:
            return self.decoders[dct['__class__']](dct)
        return dct

JSONDecoder.register(
    'datetime',
    lambda dct: datetime.datetime(
        dct['year'], dct['month'], dct['day'],
        dct['hour'], dct['minute'], dct['second'], dct['microsecond']
    )
)
JSONDecoder.register(
    'date',
    lambda dct: datetime.date(dct['year'], dct['month'], dct['day'])
)
JSONDecoder.register(
    'time',
    lambda dct: datetime.time(
        dct['hour'], dct['minute'], dct['second'], dct['microsecond']
    )
)
JSONDecoder.register(
    'timedelta',
    lambda dct: datetime.timedelta(seconds=dct['seconds'])
)


def _bytes_decoder(dct):
    cast = bytearray if bytes == str else bytes
    return cast(base64.decodestring(dct['base64'].encode('utf-8')))
JSONDecoder.register('bytes', _bytes_decoder)
JSONDecoder.register(
    'Decimal', lambda dct: Decimal(dct['decimal'])
)
JSONDecoder.register(
    'Model', lambda dct: eval(dct['repr'], {'Pool': Pool})
)


class JSONEncoder(json.JSONEncoder):

    serializers = {}

    def __init__(self, *args, **kwargs):
        super(JSONEncoder, self).__init__(*args, **kwargs)
        # Force to use our custom decimal with simplejson
        self.use_decimal = False

    @classmethod
    def register(cls, klass, encoder):
        assert klass not in cls.serializers
        cls.serializers[klass] = encoder

    def default(self, obj):
        if isinstance(obj, Model):
            marshaller = self.serializers[Model]
        else:
            marshaller = self.serializers.get(
                type(obj),
                super(JSONEncoder, self).default
            )
        return marshaller(obj)


JSONEncoder.register(
    datetime.datetime,
    lambda o: {
        '__class__': 'datetime',
        'year': o.year,
        'month': o.month,
        'day': o.day,
        'hour': o.hour,
        'minute': o.minute,
        'second': o.second,
        'microsecond': o.microsecond,
    })
JSONEncoder.register(
    datetime.date,
    lambda o: {
        '__class__': 'date',
        'year': o.year,
        'month': o.month,
        'day': o.day,
    })
JSONEncoder.register(
    datetime.time,
    lambda o: {
        '__class__': 'time',
        'hour': o.hour,
        'minute': o.minute,
        'second': o.second,
        'microsecond': o.microsecond,
    })
JSONEncoder.register(
    datetime.timedelta,
    lambda o: {
        '__class__': 'timedelta',
        'seconds': o.total_seconds(),
    })
_bytes_encoder = lambda o: {  # noqa
    '__class__': 'bytes',
    'base64': base64.encodestring(o).decode('utf-8'),
    }
JSONEncoder.register(bytes, _bytes_encoder)
JSONEncoder.register(bytearray, _bytes_encoder)
JSONEncoder.register(
    Decimal,
    lambda o: {
        '__class__': 'Decimal',
        'decimal': str(o),
    })
JSONEncoder.register(
    Model,
    lambda o: {
        '__class__': 'Model',
        'repr': repr(o),
    })


def register_serializer():
    """
    This is needed for the Kombu entry point to load encoders and decoders
    to the registry. Celery depends on Kombu for low level serialization
    from task.
    """
    from kombu.serialization import register
    register(
        'tryson',
        functools.partial(json.dumps, cls=JSONEncoder),
        functools.partial(json.loads, object_hook=JSONDecoder()),
        content_type='application/x-tryson',
        content_encoding='binary',
    )
register_serializer()
