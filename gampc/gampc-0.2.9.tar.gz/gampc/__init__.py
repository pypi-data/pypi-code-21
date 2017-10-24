# coding: utf-8
#
# Graphical Asynchronous Music Player Client
#
# Copyright (C) 2015 Itaï BEN YAACOV
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
Graphical Asyncronous Music Player Client

A Music Player Daemon client written in Python/Gtk+3, using asynchronous communication.
"""

import gi
import os
import gettext


def setup_locale():
    gettext.install('gampc', os.path.join(os.path.dirname(__file__), 'locale'))


gi.require_version('Gtk', '3.0')
gi.require_version('Peas', '1.0')
gi.require_version('PeasGtk', '1.0')

setup_locale()


__program_name__ = "Graphical Asyncronous Music Player Client"
__program_description__ = _("A Music Player Daemon client written in Python/Gtk+3, using asynchronous communication")
__author__ = "Itaï BEN YAACOV"
__copyright__ = "© 2017 " + __author__
__license__ = _("""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
""")
__version__ = '0.2.9'
