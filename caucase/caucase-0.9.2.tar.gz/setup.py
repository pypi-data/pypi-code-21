# This file is part of caucase
# Copyright (C) 2017  Nexedi
#     Alain Takoudjou <alain.takoudjou@nexedi.com>
#     Vincent Pelletier <vincent@nexedi.com>
#
# caucase is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# caucase is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with caucase.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
import glob
import os

long_description = open("README.rst").read() + "\n"
for f in sorted(glob.glob(os.path.join('caucase', 'README.*.rst'))):
  long_description += '\n' + open(f).read() + '\n'
# long_description += open("CHANGES.txt").read() + "\n"

setup(
  name='caucase',
  version='0.9.2',
  description="Certificate Authority.",
  long_description=long_description,
  classifiers=[
    'Environment :: Console',
    'Environment :: Web Environment',
    'Intended Audience :: System Administrators',
    'Intended Audience :: Information Technology',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Topic :: Security :: Cryptography',
    'Topic :: System :: Systems Administration :: Authentication/Directory',
    'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
  ],
  keywords='certificate authority',
  url='https://lab.nexedi.com/nexedi/caucase',
  license='GPLv3+',
  packages=find_packages(),
  install_requires=[
    'cryptography>=2.1.1', # everything x509 except...
    'pyOpenSSL>=17.1.0', # ...certificate chain validation
    'pem>=17.1.0', # Parse PEM files
  ],
  zip_safe=True,
  entry_points={
    'console_scripts': [
      'caucase = caucase.cli:main',
      'caucase-probe = caucase.cli:probe',
      'caucase-updater = caucase.cli:updater',
      'caucase-rerequest = caucase.cli:rerequest',
      'caucase-key-id = caucase.cli:key_id',
      'caucased = caucase.http:main',
      'caucased-manage = caucase.http:manage',
    ]
  },
  test_suite='caucase.test',
)
