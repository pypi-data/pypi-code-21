# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import re
import sys

try:
    from kopy.funcs import kopy_func
except:
    from funcs import kopy_func

class KoPy():

    def __init__(self):
        self.func = kopy_func.KoPy_func()

    def pos(self,sentences,p=0):
        if sentences == '':
            return ''
        if sentences == None:
            raise ValueError('KoPy.pos requires a not-Null string')
        result = []
        for sentence in [c.strip() for c in sentences.split('\r\n')]:
            if sys.version_info < (3,):
                sentence = unicode(sentence, 'utf-8')
            taged = self.func.pos(sentence)
            if taged:
                result.extend(self.func.pos(sentence))
            else:
                return ''
        if p:
            print(','.join(["('"+i[0]+"','"+i[1]+"')" for i in result]))
        else:
            return result

    def sentence(self,phrase,p=0):
        sent = [i.strip() for c in phrase.split('\r\n') \
                for i in re.findall('.+?(?:\.+|\?+|\!+|\"|$)(?:\.+|\?+|\!+|\")?["]?(?:라고.+?\.)?|(?:하고.+?\.)', c)]
        if p:
            print(', '.join(["('"+i+"')" for i in sent]))
        else:
            if sys.version_info < (3,):
                return [unicode(sentence, 'utf-8') for sentence in sent]
            return sent

if __name__ == "__main__":
    pass