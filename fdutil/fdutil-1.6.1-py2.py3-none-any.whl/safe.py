
__author__ = u'Hywel Thomas'
__copyright__ = u'Copyright (C) 2016 Hywel Thomas'

import os

def ascii_safe(string):
    return u''.join([c if ord(c) < 128 else u'?' for c in string])


FILE_SAFE_CHARACTERS = (u' '
                        u'1234567890-_.'
                        u'abcdefghijklmnopqrstuvwxyz'
                        u'ABCDEFGHIJKLMNOPQRSTUVWXYZ')


def file_safe(string,
              safe_char=u'_'):
    return u''.join([c if c in FILE_SAFE_CHARACTERS
                     else safe_char
                     for c in string])


def file_safe_path(path,
                   safe_char=u'_'):

    drive, path = os.path.splitdrive(path)
    path_parts = [file_safe(string=part,
                            safe_char=safe_char)
                  for part in path.replace(u'\\', u'/').split(u'/')]

    return drive + os.sep.join(path_parts)
