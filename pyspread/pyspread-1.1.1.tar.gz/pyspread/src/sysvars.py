#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright Martin Manns
# Distributed under the terms of the GNU General Public License

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""

sysvars
=======

System environment access

"""

import os

import pangocairo
import wx


# OS
def is_gtk():
    return "__WXGTK__" in wx.PlatformInfo

# Paths


def get_program_path():
    """Returns the path in which pyspread is installed"""

    src_folder = os.path.dirname(__file__)
    program_path = os.sep.join(src_folder.split(os.sep)[:-1]) + os.sep

    return program_path


def get_help_path():
    """Returns the pyspread help path"""

    return get_program_path() + "doc" + os.sep + "help" + os.sep


def get_python_tutorial_path():
    """Returns the Python tutorial path"""

    # If the OS has the Python tutorial installed locally, use it.
    # the current path is for Debian

    localpath = "/usr/share/doc/python-doc/html/tutorial/index.html"

    if os.path.isfile(localpath):
        return localpath

    else:
        return "http://docs.python.org/2/tutorial/"


# System settings

def get_mo_languages():
    """Returns list of languages, of which mo files are present"""

    return ["system"] + sorted(os.listdir(get_program_path() + "locale" +
                               os.sep))


def get_dpi():
    """Returns screen dpi resolution"""

    def pxmm_2_dpi((pixels, length_mm)):
        return pixels * 25.6 / length_mm

    return map(pxmm_2_dpi, zip(wx.GetDisplaySize(), wx.GetDisplaySizeMM()))


def get_color(name):
    """Returns system color from name"""

    return wx.SystemSettings.GetColour(name)


def get_default_font():
    """Returns default font"""

    return wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)


def get_font_string(name):
    """Returns string representation of named system font"""

    return wx.SystemSettings.GetFont(name).GetFaceName()

# Fonts


def get_font_list():
    """Returns a sorted list of all system font names"""

    font_map = pangocairo.cairo_font_map_get_default()
    font_list = [f.get_name() for f in font_map.list_families()]
    font_list.sort()

    return font_list


def get_default_text_extent(text):
    """Returns the text extent for the default font"""

    return wx.GetApp().GetTopWindow().GetTextExtent(text)


def get_dependencies():
    """Returns list of dicts which indicate installed dependencies"""

    dependencies = []

    # Numpy
    dep_attrs = {
        "name": "numpy",
        "min_version": "1.1.0",
        "description": "required",
    }
    try:
        import numpy
        dep_attrs["version"] = numpy.version.version
    except ImportError:
        dep_attrs["version"] = None
    dependencies.append(dep_attrs)

    # wxPython
    dep_attrs = {
        "name": "wxPython",
        "min_version": "2.8.10.1",
        "description": "required",
    }
    try:
        import wx
        dep_attrs["version"] = wx.version()
    except ImportError:
        dep_attrs["version"] = None
    dependencies.append(dep_attrs)

    # Matplotlib
    dep_attrs = {
        "name": "matplotlib",
        "min_version": "1.1.1",
        "description": "required",
    }
    try:
        import matplotlib
        dep_attrs["version"] = matplotlib._version.get_versions()["version"]
    except ImportError:
        dep_attrs["version"] = None
    except AttributeError:
        # May happen in old matplotlib versions
        dep_attrs["version"] = matplotlib.__version__

    dependencies.append(dep_attrs)

    # Pycairo
    dep_attrs = {
        "name": "pycairo",
        "min_version": "1.8.8",
        "description": "required",
    }
    try:
        import cairo
        dep_attrs["version"] = cairo.version
    except ImportError:
        dep_attrs["version"] = None
    dependencies.append(dep_attrs)

    # Python GnuPG
    dep_attrs = {
        "name": "python-gnupg",
        "min_version": "0.3.0",
        "description": "for opening own files without approval",
    }
    try:
        import gnupg
        dep_attrs["version"] = gnupg.__version__
    except ImportError:
        dep_attrs["version"] = None
    dependencies.append(dep_attrs)

    # xlrd
    dep_attrs = {
        "name": "xlrd",
        "min_version": "0.9.2",
        "description": "for loading Excel files",
    }
    try:
        import xlrd
        dep_attrs["version"] = xlrd.__VERSION__
    except ImportError:
        dep_attrs["version"] = None
    dependencies.append(dep_attrs)

    # xlwt
    dep_attrs = {
        "name": "xlwt",
        "min_version": "0.7.2",
        "description": "for saving Excel files",
    }
    try:
        import xlwt
        dep_attrs["version"] = xlwt.__VERSION__
    except ImportError:
        dep_attrs["version"] = None
    dependencies.append(dep_attrs)

    # Jedi
    dep_attrs = {
        "name": "jedi",
        "min_version": "0.8.0",
        "description": "for tab completion and context help in the entry line",
    }
    try:
        import jedi
        dep_attrs["version"] = jedi.__version__
    except ImportError:
        dep_attrs["version"] = None
    dependencies.append(dep_attrs)

    # pyrsvg
    dep_attrs = {
        "name": "pyrsvg",
        "min_version": "2.32",
        "description": "for displaying SVG files in cells",
    }
    try:
        import rsvg
        dep_attrs["version"] = True
    except ImportError:
        dep_attrs["version"] = None
    dependencies.append(dep_attrs)

    # pyenchant
    dep_attrs = {
        "name": "pyenchant",
        "min_version": "1.6.6",
        "description": "for spell checking",
    }
    try:
        import enchant
        dep_attrs["version"] = enchant.__version__
    except ImportError:
        dep_attrs["version"] = None
    dependencies.append(dep_attrs)

    return dependencies
