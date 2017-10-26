# -*- coding: utf-8 -*-
import sys

PY2 = int(sys.version_info[0]) == 2

if PY2:
    import urlparse
    import urllib

    urlparse = urlparse
    urlencode = urllib.urlencode
    text_type = unicode
    binary_type = str
    string_types = (str, unicode)
    unicode = unicode
    basestring = basestring
    iterkeys = lambda d: d.iterkeys()
    itervalues = lambda d: d.itervalues()
    iteritems = lambda d: d.iteritems()
else:
    import urllib.parse

    urlparse = urllib.parse
    urlencode = urllib.parse.urlencode
    text_type = str
    binary_type = bytes
    string_types = (str,)
    unicode = str
    basestring = (str, bytes)
    iterkeys = lambda d: d.keys()
    itervalues = lambda d: d.values()
    iteritems = lambda d: d.items()
