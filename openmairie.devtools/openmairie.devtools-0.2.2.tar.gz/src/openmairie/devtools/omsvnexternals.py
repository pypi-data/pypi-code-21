#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import shutil
import subprocess
from glob import glob


class OMSVNExternals(object):
    """
    """
    def main(self):
        """
        """
    #
    externals = []
    #
    for result in [y for x in os.walk('.') for y in glob(os.path.join(x[0], 'EXTERNALS.txt'))]:
        #
        print result
        #
        path_root = os.path.relpath(os.path.join(result, os.pardir))
        #
        text = open(result).readlines()
        for x in text:
            if x.strip().startswith('#'):
                continue
            if not x.strip():
                continue
            if x.strip() == '\n':
                continue
            external = x.replace('\n', '').split()
            externals.append({"dest": path_root + "/" + external[0], "src": external[1]})
    #
    print externals
    #
    for external in externals:
        print external["dest"]
        # if os.path.exists(external["dest"]):
        #     print "remove folder " + external["dest"]
        #     shutil.rmtree(external["dest"])
        print "svn export " + external["src"]
        subprocess.check_call(["svn", "export", external["src"], external["dest"]])


def main():
    svnexternals = OMSVNExternals()
    svnexternals.main()
