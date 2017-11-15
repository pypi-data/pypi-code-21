#!/usr/bin/env python

from __future__ import print_function
import glob
from opster import command, dispatch
from sh import twine, python, rm

@command()
def upload(fn = '', repo = ('r', 'test', 'repository to upload to')):
    if not fn:
        fns = glob.glob('dist/*.tar.gz')
        fns.sort()
        fn = fns[-1]
    print(twine.upload(fn, r=repo))

@command()
def package():
    print(python('setup.py', 'sdist'))

@command()
def clean():
    print(rm('-r', 'dist', 'dionysus.egg-info'))

if __name__ == '__main__':
    dispatch()




