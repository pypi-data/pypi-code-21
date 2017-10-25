#!/usr/bin/env python
import cPickle as pickle
import sys
from io import open

from pypinyin.contrib.mmseg import PrefixSet, Seg

pset = PrefixSet()
seg = Seg(pset)


def max_match_segment( line, dic ):
    # write your code here
    pset.train(list(dic))
    return list(seg.cut(line))

if __name__=="__main__":

    try:
        fpi=open(sys.argv[1], "r")
    except:
        print >> sys.stderr, "failed to open file"
        sys.exit(1)

    try:
        dic = pickle.load(open(sys.argv[2]))
        dic = (x.decode('utf-8') for x in dic)
    except:
        print >> sys.stderr, "failed to load dict"
        sys.exit(1)

    with open(sys.argv[3], 'w', encoding='utf-8') as output:
        for line in fpi:
            output.write("\t".join( max_match_segment(line.strip(), dic)))
            output.write(u'\n')
