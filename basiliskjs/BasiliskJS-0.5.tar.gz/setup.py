#!/usr/bin/python3
# coding: utf8

from setuptools import setup, find_packages
from os.path import join, dirname
import basilisk

setup(
	name = basilisk.__title__,
	version = basilisk.__version__,
	description = 'Web browser emulator, based on PhantomJS',
	long_description = open(join(dirname(__file__), 'README.rst')).read(),
	url = 'https://github.com/lich666dead/BasiliskJS',
	download_url = 'https://github.com/lich666dead/BasiliskJS/archive/master.zip',
	license = 'GNU General Public License v3 (GPLv3)',
	author = basilisk.__author__,
	author_email = 'lich666black@gmail.com',
	maintainer = basilisk.__author__,
	platforms = 'any',
	packages = find_packages(),
    zip_safe = False,
	package_dir = {'basilisk': 'basilisk'},
	include_package_data = True,
	classifiers = [
		'Environment :: Web Environment',
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
		'Natural Language :: Russian',
		'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
)
