# coding: utf-8

# Asynchronous Music Player Daemon client library for Python

# Copyright (C) 2015 Itaï BEN YAACOV

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
Asynchronous MPD client library
"""


from . import errors
from ._request import Event
from ._client import task, Task, Client, ServerProperties


__author__ = "Itaï BEN YAACOV"
__copyright__ = "© 2017 " + __author__
__version__ = '0.2.8'

__all__ = [
    '__author__',
    '__copyright__',
    '__version__',
    'errors',
    'Event',
    'task',
    'Task',
    'Client',
    'ServerProperties',
]

globals().update(Event.__members__)
__all__ += list(Event.__members__.keys())

try:
    from ._glib import ClientGLib, ServerPropertiesGLib
    __all__ += [
        'ClientGLib',
        'ServerPropertiesGLib',
    ]
except:
    pass
