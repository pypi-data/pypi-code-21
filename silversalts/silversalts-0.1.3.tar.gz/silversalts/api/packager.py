import json
import zlib
import base64


SUPPORTED_OPTIONS = [
    'version',
    'data',
    'input_scheme',
    'output_scheme',
    'use_cache',
    # tesseract
    'psm',
    'oem',
    'lang',
    # output
    'text_visible',
    'orig_visible',
    'text_color',
    'text_color_reflects_cl',
]
SUPPORTED_LANG = [
    'eng',
    'deu',
    'fra',
    'spa',
    'jpn',
    'chi_tra',
    'chi_sim',
    'ita',
    'por',
    'nld',
    'hin',
]
SUPPORTED_INPUT_SCHEME = ['raw', 's3']
SUPPORTED_OUTPUT_SCHEME = ['hocr', 'pdf']


class Packager(object):
    def __init__(self, crypter, **kwargs):
        self._crypter = crypter
        self._compress_level = kwargs.get('compress_level', 9)

    def pack(self, data, key):
        assert isinstance(data, str), 'invalid data, must be an ascii string'
        crypted = self._crypter.encode(data, key)
        crushed = zlib.compress(crypted, self._compress_level)
        encoded = base64.urlsafe_b64encode(crushed)
        return encoded

    def unpack(self, data, key):
        assert isinstance(data, str), 'invalid data, must be an ascii string'
        decoded = base64.urlsafe_b64decode(data)
        widened = zlib.decompress(decoded)
        cracked = self._crypter.decode(widened, key)
        return cracked

class JsonPackager(Packager):
    def __init__(self, crypter, **kwargs):
        super(JsonPackager, self).__init__(crypter, **kwargs)

    def pack(self, data, key):
        text = json.dumps(data)
        return super(JsonPackager, self).pack(text, key)

    def unpack(self, data, key):
        text = super(JsonPackager, self).unpack(data, key)
        return json.loads(text)

class SilverSaltsPackager(JsonPackager):
    def __init__(self, crypter, **kwargs):
        super(SilverSaltsPackager, self).__init__(crypter, **kwargs)

    def pack(self, data, key):
        if not isinstance(data, dict):
            raise ValueError('Error: spec must be a dictionary')
        if 'input_scheme' in data and data['input_scheme'] not in SUPPORTED_INPUT_SCHEME:
            raise ValueError('Error: input scheme only supports the listed: %s' % (
                ', '.join(SUPPORTED_INPUT_SCHEME)
            ))
        if 'output_scheme' in data and data['output_scheme'] not in SUPPORTED_OUTPUT_SCHEME:
            raise ValueError('Error: output scheme only supports the listed: %s' % (
                ', '.join(SUPPORTED_OUTPUT_SCHEME)
            ))
        if 'lang' in data and any([l not in SUPPORTED_LANG for l in data['lang']]):
            raise ValueError('Error: lang only supports the listed: %s' % (
                ', '.join(SUPPORTED_LANG)
            ))
        for k in data.keys():
            if k not in SUPPORTED_OPTIONS:
                raise ValueError('Error: %s is not one of the supported keys (%s)' % (
                    k,
                    ', '.join(SUPPORTED_OPTIONS)
                ))
        data['data'] = base64.b64encode(data['data'])
        return super(SilverSaltsPackager, self).pack(data, key)

    def unpack(self, data, key):
        data = super(SilverSaltsPackager, self).unpack(data, key)
        data['data'] = base64.b64decode(data['data'])
        return data
