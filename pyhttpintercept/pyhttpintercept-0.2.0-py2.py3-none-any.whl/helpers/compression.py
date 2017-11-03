
import gzip
import StringIO
import logging_helper

logging = logging_helper.setup_logging()


# Export constants
class _METHODS:

    def __init__(self): pass

    # Available compression methods
    @property
    def gzip(self): return u'gzip'

    @property
    def zlib(self): return u'zlib'

CMP_METHODS = _METHODS()  # Initialise Constants

_available_methods = [
    CMP_METHODS.gzip,
    CMP_METHODS.zlib
]


# Exceptions
class CompressionMethodNotFound(Exception):
    pass


# Compression Functions
def _compress_gzip(source):

    """
    http://stackoverflow.com/a/8507012/2916546
    """

    try:
        source = bytes(source)

    except UnicodeEncodeError:
        source = bytes(source.encode(u'utf-8'))

    out = StringIO.StringIO()

    with gzip.GzipFile(fileobj=out,
                       mode=u"wb",
                       compresslevel=9) as f:
        f.write(source)

    out.getvalue()

    compressed = out.buf

    logging.info(u'Original size:{len_source}; GZIP Compressed size:{len_compressed}'
                 .format(len_source=len(source),
                         len_compressed=len(compressed)))

    return compressed


def _compress_zlib(source):

    compressed = source.encode(u'utf-8').encode(u'zlib_codec')  # decoding:object.decode(u'zlib_codec').decode(u'utf-8')
    logging.info(u'Original size:{len_source}; ZLIB Compressed size:{len_compressed}'
                 .format(len_source=len(source),
                         len_compressed=len(compressed)))
    return compressed


# Export Method -> function associations
_method_functions = {
    CMP_METHODS.gzip: _compress_gzip,
    CMP_METHODS.zlib: _compress_zlib
}


# Define the interface
def compress(source,
             method=CMP_METHODS.gzip):

    if method not in _available_methods:
        raise CompressionMethodNotFound(u'Compression method {method} is not available.'.format(method=method))

    compression_fn = _method_functions.get(method)

    return compression_fn(source)
