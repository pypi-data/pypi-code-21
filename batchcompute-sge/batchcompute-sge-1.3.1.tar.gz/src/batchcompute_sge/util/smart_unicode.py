# -*- coding: utf-8 -*-

import locale
import codecs


import sys

# Python 2 or Python 3 is in use.
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


try:
    import unicode
except:
    def unicode(s,encode):
        return s.decode(encode)

def get_locale():
    return codecs.lookup(locale.getpreferredencoding()).name

if PY2:
    reload(sys)
    sys.setdefaultencoding(get_locale())

def format_utf8(string):
    if PY3:
        return string
    else:
        return smart_code(string).encode(get_locale())


def smart_code(input_stream):

    if isinstance(input_stream, str):
        try:
            tmp = unicode(input_stream, 'utf-8')
        except UnicodeDecodeError:
            try:
                tmp = unicode(input_stream, 'gbk')
            except UnicodeDecodeError:
                try:
                    tmp = unicode(input_stream, 'gb2312')
                except UnicodeDecodeError:
                    try:
                        tmp = unicode(input_stream, 'big5')
                    except UnicodeDecodeError:
                        try:
                            tmp = unicode(input_stream, 'ascii')
                        except:
                            tmp = input_stream
    else:
        tmp = input_stream
    return tmp


if __name__ == '__main__':
    print(format_utf8("啊"))