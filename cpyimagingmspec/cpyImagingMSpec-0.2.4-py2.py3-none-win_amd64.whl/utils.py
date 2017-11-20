import platform
import os.path

import cffi
import numbers
import numpy as np

_ffi = None
_ims = None

def full_filename(fn):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), fn))

def shared_lib(name):
    suffixes = {'Windows': 'dll', 'Linux': 'so', 'Darwin': 'dylib'}
    return 'lib' + name + '.' + suffixes[platform.system()]

def init_ffi():
    global _ffi
    if _ffi is None:
        _ffi = cffi.FFI()
        _ffi.cdef(open(full_filename("ims.h")).read())
    return _ffi

def load_shared_lib():
    global _ims
    if _ims is None:
        ffi = init_ffi()
        _ims = ffi.dlopen(full_filename(shared_lib("ims_cffi")))
    return _ims

_has_numpy = True
_dtypes = {'f': np.float32, 'd': np.float64}
_full_types = {'f': 'float', 'd': 'double'}

def _as_buffer(array, numtype):
    return np.asarray(array, dtype=_dtypes[numtype])

class cffi_buffer(object):
    def __init__(self, n, numtype):
        if isinstance(n, numbers.Number):
            self.buf = np.zeros(n, dtype=_dtypes[numtype])
        else:
            self.buf = _as_buffer(n, numtype)

        self.ptr = _ffi.cast(_full_types[numtype] + '*',
                             self.buf.__array_interface__['data'][0])

    def python_data(self):
        return self.buf

def raise_ims_exception():
    raise Exception(_ffi.string(_ims.ims_strerror()))

def raise_ims_exception_if_null(arg):
    if arg == _ffi.NULL:
        raise_ims_exception()

VERSION = "0.2.4"
