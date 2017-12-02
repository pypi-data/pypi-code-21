#!/usr/bin/env python

from setuptools import setup

setup(
    name = 'hotmic'
    ,version = '0.1.6'
    ,author = 'frank2'
    ,author_email = 'frank2@dc949.org'
    ,description = 'A Galois LFSR implementation with lots of polys.'
    ,license = 'GPLv3'
    ,keywords = 'lfsr'
    ,url = 'https://github.com/frank2/hotmic'
    ,package_dir = {'hotmic': 'lib'}
    ,packages = ['hotmic']
    ,long_description = '''hotmic is simply an LFSR library with polys pulled from
this document: http://web.archive.org/web/20161007061934/http://courses.cse.tamu.edu/csce680/walker/lfsr_table.pdf.'''
    ,classifiers = [
        'Development Status :: 3 - Alpha'
        ,'Topic :: Software Development :: Libraries'
        ,'License :: OSI Approved :: GNU General Public License v3 (GPLv3)']
)
