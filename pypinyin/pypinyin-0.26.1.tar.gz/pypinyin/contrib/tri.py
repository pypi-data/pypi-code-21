# -*- coding: utf-8 -*-
from pprint import pprint
from collections import defaultdict

a_dict_str = u'''
a
ab
abc
abcd
abd
ac
acd
aff
agf
agfgef
中国
中国人
中国人民
中国人民银行
我
北京
天安门
'''


def tree():
    return defaultdict(tree)


tri = defaultdict(tree)


def build_tri(u_dict_str):
    words = sorted(filter(None, (x.strip() for x in u_dict_str.split('\n'))))
    for word in words:
        pre = tri[word[0]]
        for w in word[1:]:
            pre = pre[w]
        pre['__end'] = True


def contains(s):
    pre = tri
    for x in s:
        if x not in pre:
            return False
        pre = pre[x]
    if pre['__end'] or not pre:
        return True


def seg(s):
    print 'start', s
    max_length = 10
    while s:
        if len(s) < max_length:
            max_length = len(s)
        orig = s[:max_length]
        while not contains(orig):
            if len(orig) == 1:
                break
            else:
                orig = orig[:-1]
        yield orig
        s = s[len(orig):]


build_tri(a_dict_str)
pprint(tri)

print(a_dict_str)
s = u'abcadbasfgafgasdabcagfaff我是中国人中国人民我爱北京天安门'
for x in seg(s):
    print(x)

