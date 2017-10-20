# Copyright 2008-2015 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.config.
#
# lazr.config is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# lazr.config is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lazr.config.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

with open('src/lazr/config/_version.py') as version_file:
    exec(version_file.read())  # sets __version__

setup(
    name='lazr.config',
    version=__version__,
    namespace_packages=['lazr'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    maintainer='LAZR Developers',
    maintainer_email='lazr-developers@lists.launchpad.net',
    description=('Create configuration schemas, and process and '
                 'validate configurations.'),
    long_description="""
The LAZR config system is typically used to manage process configuration.
Process configuration is for saying how things change when we run systems on
different machines, or under different circumstances.

This system uses ini-like file format of section, keys, and values.  The
config file supports inheritance to minimize duplication of information across
files. The format supports schema validation.
""",
    license='LGPL v3',
    install_requires=[
        'setuptools',
        'zope.interface',
        'lazr.delegates',
        ],
    url='https://launchpad.net/lazr.config',
    download_url='https://launchpad.net/lazr.config/+download',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        ],
    )
