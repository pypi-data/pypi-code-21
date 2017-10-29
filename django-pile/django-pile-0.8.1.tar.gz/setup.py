#!/usr/bin/env python
#
# Copyright (C) 2010 Martin Owens
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
import os
import sys

from setuptools import setup
from pile import __version__

# remove MANIFEST. distutils doesn't properly update it when the contents of directories change.
if os.path.exists('MANIFEST'): os.remove('MANIFEST')

setup(
    name             = 'django-pile',
    version          = __version__,
    release          = "",
    description      = 'A pile of django code for common use over multiple websites.',
    long_description = "Contains some very useful common abstractions for django.",
    author           = 'Martin Owens',
    url              = 'https://github.com/doctormo/django-pile',
    author_email     = 'doctormo@gmail.com',
    platforms        = 'linux',
    license          = 'AGPLv3',
    py_modules       = ['pile', 'pile.templatetags'],
)

