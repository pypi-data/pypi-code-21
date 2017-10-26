#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, print_function, unicode_literals

import sys, os
from distutils.core import setup
from distutils.extension import Extension
import struct
PY2 = sys.version_info[0] == 2
if PY2:
    # Py3 compatibility
    from io import open
    str = unicode
    chr = unichr
    range = xrange
    input = raw_input
    import itertools
    filter = itertools.ifilter
    map = itertools.imap
    zip = itertools.izip
    
    nativestring = bytes
else:
    nativestring = str

# Py2.6 requires a byte string
_PY_BIT = struct.calcsize(b'P') * 8

dir = os.path.abspath(os.path.dirname(__file__))

# Read package description
with open(os.path.join(dir, 'README.txt'), 'rt', encoding='utf-8') as fh:
    readme = fh.read()

package_data = {
    nativestring('kontocheck'): ['data/blz.lut2', 'data/scl.csv'],
    }
        
if os.name == 'nt':
    package_data['kontocheck'].append('lib/kontocheck%s.dll' % _PY_BIT)
    ext_modules = None
else:
    # distutils requires native string types
    ext_modules = [
        Extension(nativestring('kontocheck.lib.kontocheck'),
            sources=[nativestring('lib/konto_check/konto_check.c')],
            libraries=[nativestring('z')],
        ),
    ]

dist = setup(
    name='kontocheck',
    version='6.01.0',
    author='Thimo Kraemer',
    author_email='thimo.kraemer@joonis.de',
    url='http://www.joonis.de/software/fintech/kontocheck',
    description='Python ctypes wrapper of the konto_check library.',
    long_description=readme,
    keywords=('kontocheck', 'iban', 'bic', 'scl'),
    download_url='',
    license='LGPLv3',
    ext_modules=ext_modules,
    package_dir={'kontocheck': 'src'},
    packages=[nativestring('kontocheck')],
    package_data=package_data,
    classifiers=[
        'Topic :: Office/Business :: Financial',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        ],
    )
