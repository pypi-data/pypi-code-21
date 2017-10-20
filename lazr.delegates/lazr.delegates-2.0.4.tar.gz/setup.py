# Copyright 2008-2015 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.delegates.
#
# lazr.delegates is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# lazr.delegates is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lazr.delegates.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

with open('lazr/delegates/_version.py') as version_file:
    exec(version_file.read())  # sets __version__

setup(
    name='lazr.delegates',
    version=__version__,
    namespace_packages=['lazr'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    maintainer='LAZR Developers',
    maintainer_email='lazr-developers@lists.launchpad.net',
    description='Easily write objects that delegate behavior',
    long_description="""
The ``lazr.delegates`` package makes it easy to write objects that delegate
behavior to another object. The new object adds some property or behavior on
to the other object, while still providing the underlying interface, and
delegating behavior.
""",
    license='LGPL v3',
    install_requires=[
        'nose',
        'setuptools',
        'zope.interface',
        ],
    url='https://launchpad.net/lazr.delegates',
    download_url= 'https://launchpad.net/lazr.delegates/+download',
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
    # nose plugins don't really work with `python setup.py test` so use
    # `python setup.py nosetests` instead, or just `tox`.  Gosh, we really
    # should switch to nose2. :/  - BAW 2014-08-20
    #test_suite='nose.collector',
    )
