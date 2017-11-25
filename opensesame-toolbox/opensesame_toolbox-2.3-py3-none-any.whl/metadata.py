# -*- coding: utf-8 -*-
"""
This file is part of OpenSesame Toolbox

OpenSesame Toolbox is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame Experiment Manager is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

Refer to <http://www.gnu.org/licenses/> for a copy of the GNU General Public License.

@author Bob Rosbag
"""

from distutils.version import StrictVersion
from libopensesametoolbox import metadata
import sys

__version__ = u'2.3'
strict_version = StrictVersion(__version__)
# The version without the prerelease (if any): e.g. 3.0.0
main_version = '.'.join([str(i) for i in strict_version.version])
# The version following the debian convention: e.g. 3.0.0~a1
if strict_version.prerelease is None:
	deb_version = main_version
else:
	deb_version = main_version + '+%s%d' % strict_version.prerelease
python_version = '%d.%d.%d' % sys.version_info[:3]
codename = 'Kitschy Kuhn'
channel = 'dev'
api = StrictVersion('2.1')
platform = sys.platform
