#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Find or remove (do not remove, just generate a script used to remove) files that include
the specified keyword.
"""

__authors__ = 'teachmyself@126.com'
__license__ = 'MIT License'
__version__ = '0.0.1'

import time
import argparse

import cmstop
from common import *


def find(keyword, path="./"):
    """
    Find files that contains the keyword.
    """
    is_dir(path)
    cmd = ' '.join(["grep", keyword, '-rl', path])
    res = os.popen(cmd, "r")
    return res

def find_cmd(keyword, path="./"):
    """
    Find files that contains the keyword in command line.
    """
    res = find(keyword, path).readlines()
    count = len(res)
    print "%d files contains \"%s\" founded in directory %s." % (count, keyword, path)
    print ''
    if count == 0:
        sys.exit(0)
    for f in res:
        print f,

def find_backup(keyword, path="./"):
    """
    Backup files that contains the keyword.
    """
    os.chdir(path)
    res = find(keyword, './').readlines()
    count = len(res)
    print "%d files contains \"%s\" founded in directory %s." % (count, keyword, path)
    print ''
    for file in res:
        bkfile = '.'.join([keyword, time.strftime("%F_%T").replace(":","-"), "tar.gz"])
        cmd = ' '.join(["tar", "-rvf", "/tmp/"+bkfile, file])
        res = os.popen(cmd, "r")
        print res.read(),

def find_remove(keyword, path="./", script="/tmp/cmstop-remove.sh"):
    """
    Creaet a script that can be used to remove files contains keyword.
    """
    res = find(keyword, path).readlines()
    count = len(res)
    print "%d files contains \"%s\" founded in directory %s." % (count, keyword, path)
    print ''
    with open(script, "wb") as sh:
        sh.write("#!/bin/bash\n")
    os.chmod(script, 666)
    for file in res:
        remove_cmd = ' '.join(["rm -rf", file])
        with open(script, "ab") as sh:
            sh.write(remove_cmd)
        print remove_cmd,

def process_args(argv):
    """
    Process argument from command line.
    """
    parser = argparse.ArgumentParser(
	version=" ".join(["%(prog)s", __version__]),
	description="Find files that contains the keywords.")

    parser.add_argument(
        "-k", "--keyword", action="store", dest="keyword", default="",
        help="specified a keyword to find")
    parser.add_argument(
	"-p", "--path", action="store", dest="path", default=".",
        help="specified a path to find, such as /path/to/xxx, defualt: current directory as .")
    parser.add_argument(
        "-b", "--backup", action="store_true", dest="backup", default=False,
        help="backup files found by keyword to /tmp/KEYWORD.DATETIME.tar.gz")
    parser.add_argument(
        "-r", "--remove", action="store_true", dest="remove", default=False,
        help="create remove script in /tmp/%(prog)s.sh")

    results = parser.parse_args(argv)
    return results


def main():
    results = process_args(sys.argv[1:])
    if results.keyword == "":
        print "Should specified keyword by -k or --keyword option"
        process_args(["-h"])
	sys.exit(1)
    if results.backup:
        find_backup(results.keyword, results.path)
    if results.remove:
        find_remove(results.keyword, results.path)
    find_cmd(results.keyword, results.path)

if __name__ == "__main__":
    main()
