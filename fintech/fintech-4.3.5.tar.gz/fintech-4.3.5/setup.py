#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, print_function, unicode_literals

import sys, os
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
    
    from urllib import URLopener
else:
    nativestring = str
    
    from urllib.request import URLopener
try:
    from setuptools import setup, Extension
    from setuptools.command.build_ext import build_ext as _build_ext
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension
    from distutils.command.build_ext import build_ext as _build_ext
from zipfile import ZipFile
import platform
import locale
import struct

PKG_VERSION = '4.3.5'

dir = os.path.abspath(os.path.dirname(__file__))

show_license = False # temporarily disabled
#if '--license-accepted' in sys.argv:
    #show_license = False
    #sys.argv.remove('--license-accepted')
#else:
    #show_license = True

class build_ext(_build_ext):
    
    def build_extension(self, ext):
        if ext.language != 'download':
            return _build_ext.build_extension(self, ext)
        
        # Check local dist directory first
        zip_path = os.path.join(dir, 'dist', ext.sources[0].split('/')[-1])
        if not os.path.isfile(zip_path):
            # Download the extension
            print('Downloading %s extension ...' % ext.name)
            sys.stdout.flush() # required to show up in pip
            opener = URLopener()
            try:
                zip_path, headers = opener.retrieve(ext.sources[0])
            except IOError as err:
                if PY2:
                    errmsg, status, statmsg, headers = err
                else:
                    status = err.code
                if status == 404:
                    sys.exit('Sorry, platform or Python version not supported.')
                raise
        # Get destination path and extension name
        ext_path = self.get_ext_fullpath(ext.name)
        ext_dir, ext_name = os.path.split(ext_path)
        # Get language
        lang = locale.getdefaultlocale()[0] or 'en'
        lang = lang.split('_')[0]
        zip = ZipFile(zip_path)
        try:
            if show_license:
                # Get and show license
                members = zip.namelist()
                for suffix in ('_'+lang, '_en', ''):
                    licensefile = 'license%s.txt' % suffix
                    if licensefile in members:
                        text = zip.read(licensefile).strip()
                        text = text.decode('utf-8')
                        print('\n%s\n' % ('*' * 76))
                        print(text)
                        print('\n%s\n' % ('*' * 76))
                        print('Do you accept the license? [y/N]: ')
                        sys.stdout.flush() # required to show up in pip
                        accepted = input('').strip()
                        if not accepted.lower().startswith('y'):
                            sys.exit('Aborted')
                        break
            # Finally extract the extension
            zip_member = ext.name + os.path.splitext(ext_name)[1]
            zip.extract(zip_member, ext_dir)
            if zip_member != ext_name:
                os.rename(os.path.join(ext_dir, zip_member), ext_path)
        finally:
            zip.close()


# Read package description
with open(os.path.join(dir, 'README.txt'), 'rt', encoding='utf-8') as fh:
    readme = fh.read()

# fintech extension to download
# distutils requires native string types
extension = Extension(nativestring('fintech'), [nativestring(
        'http://www.joonis.de/pyfintech/v%s/fintech-%s-py%s-ucs%i-%s-%sbit.zip' % (
        PKG_VERSION,
        PKG_VERSION,
        '%i.%i' % sys.version_info[:2],
        sys.maxunicode == 0xffff and 2 or 4, # UCS-2 or UCS-4
        platform.system().lower(),
        struct.calcsize(b'P') * 8, # Py2.6 requires a byte string
    ))], language='download')

setup(
    name='fintech',
    version=PKG_VERSION,
    author='Thimo Kraemer',
    author_email='thimo.kraemer@joonis.de',
    url='http://www.joonis.de/software/fintech',
    description='The Python FinTech package (SEPA, EBICS & more)',
    long_description=readme,
    keywords=('fintech', 'ebics', 'sepa', 'swift', 'mt940', 'camt', 'pain', 'iban', 'datev'),
    license='Proprietary, see http://www.joonis.de/software/fintech/license',
    cmdclass={'build_ext': build_ext},
    ext_modules=[extension],
    install_requires=['lxml', 'certifi', 'fpdf>=1.7.2'],
    zip_safe=False,
    classifiers=[
        'Topic :: Office/Business :: Financial',
        'Topic :: Office/Business :: Financial :: Accounting',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'License :: Free To Use But Restricted',
        ],
)
