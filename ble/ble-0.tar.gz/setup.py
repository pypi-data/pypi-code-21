__author__ = 'Nathan L. Conrad'
__copyright__ = 'Copyright 2017 ALT-TEKNIK LLC'
__license__ = '''GNU Lesser General Public License, Version 3

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.'''
__version__ = 0

from setuptools import find_packages, setup

setup(
    name='ble',
    version=__version__,
    author=__author__,
    author_email='nathan@noreply.alt-teknik.com',
    license=__license__,
    description='Library to simplify interaction with Bluetooth LE '
        'controllers and OS frameworks',
    url='https://pypi.python.org/pypi/ble',
    packages=find_packages()
    )
