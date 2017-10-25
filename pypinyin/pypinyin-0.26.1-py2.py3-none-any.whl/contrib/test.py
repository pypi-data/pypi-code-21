# coding: utf-8

import mmseg
s = mmseg.seg
print(list(s.cut(u'北京天安天安门北京xy')))
print(list(s.cut(u'x天安门北京xy')))
print(list(s.cut(u'xxy')))
