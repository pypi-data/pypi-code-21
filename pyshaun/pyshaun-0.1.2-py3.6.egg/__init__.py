__version__ = '0.1.1'
__all__ = [ 'load', 'load_file', 'dump', 'Numeric' ]

from .decoder import SHAUNDecoder
from .prettyprinter import SHAUNPP
from .numeric import Numeric

def load_file(fp, **kwargs):
    try:
        f = open(str(fp), 'r')
        return load(f.read(), **kwargs)
    except:
        return load(fp.read(), **kwargs)

def load(s, **kwargs):
    dec = SHAUNDecoder(s, **kwargs)
    return dec.decode()

def dump(sn):
    return SHAUNPP(sn).dump()
