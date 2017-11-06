import sys
_PY3 = sys.version_info[0] == 3

if _PY3:
    long = int
    unicode = str
    xrange = range
    integer_types = (int,)
    basestring = str
    import binascii
    byteshex = lambda b: binascii.hexlify(b)
    bytesunhex = lambda b: binascii.unhexlify(b)

    def v_iteritems(d):
        return d.items()

else:

    byteshex = lambda b: b.encode("hex")
    bytesunhex = lambda b: b.decode("hex")
    xrange = xrange
    integer_types = (int, long)

    def v_iteritems(d):
        return d.iteritems()
