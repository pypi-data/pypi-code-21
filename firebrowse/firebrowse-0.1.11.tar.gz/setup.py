#===============================================================================
# The Broad Institute
# SOFTWARE COPYRIGHT NOTICE AGREEMENT
# This software and its documentation are copyright 2015-2017 by the
# Broad Institute/Massachusetts Institute of Technology. All rights are reserved.
#
# This software is supplied without any warranty or guaranteed support whatsoever. Neither
# the Broad Institute nor MIT can be responsible for its use, misuse, or functionality.
# 
#===============================================================================

import os
from setuptools import setup, find_packages

#===============================================================================
# Setup
#===============================================================================

if os.path.exists('README'):
    README = open('README').read()
    README = README.replace('&nbsp;','')
    README = README.replace('**','')
else:
    README = 'firebrowse : Python client bindings for firebrowse RESTful API'\
             'Generated 2017_10_31__21_30_27 EDT'

setup(
    name         = 'firebrowse',
    version      = '0.1.11',
    author       = 'Michael S. Noble, via fbgen code generator',
    author_email = 'gdac@broadinstitute.org',
    url          = 'http://firebrowse.org/api/api-docs',
	license      = 'Broad Institute, MIT/BSD-style',
    packages     = find_packages(),
    description  = ('firebrowse portal API bindings for Python'),
    long_description = README,
    entry_points  = {
		'console_scripts': [
			'fbget = firebrowse.highlevel:main',
            'fbgen = firebrowse.generate:main'
		]
	},
    test_suite   = 'nose.collector',
	install_requires = [
        'requests',
        'future',
    ],
    package_data = {'':['VERSION','LICENSE.txt','template.setup']}
)
