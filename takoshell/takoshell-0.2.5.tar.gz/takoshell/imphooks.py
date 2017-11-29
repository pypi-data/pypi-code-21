# This file is part of tako
# Copyright (c) 2015-2017 Adam Hartz <hartz@mit.edu> and contributors
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# tako is a fork of xonsh (http://xon.sh)
# xonsh is Copyright (c) 2015-2016 the xonsh developers and is licensed under
# the 2-Clause BSD license.

# -*- coding: utf-8 -*-
"""Import hooks for importing tako source files.

This module registers the hooks it defines when it is imported.
"""
import builtins
from importlib.abc import MetaPathFinder, SourceLoader
from importlib.machinery import ModuleSpec
import os
import sys

from takoshell.execer import Execer
from takoshell.platform import scandir


class TakoImportHook(MetaPathFinder, SourceLoader):
    """Implements the import hook for tako source files."""

    def __init__(self, *args, **kwargs):
        super(TakoImportHook, self).__init__(*args, **kwargs)
        self._filenames = {}
        self._execer = None

    @property
    def execer(self):
        if hasattr(builtins, '__tako_execer__'):
            execer = builtins.__tako_execer__
            if self._execer is not None:
                self._execer = None
        elif self._execer is None:
            self._execer = execer = Execer(unload=False)
        else:
            execer = self._execer
        return execer

    #
    # MetaPathFinder methods
    #
    def find_spec(self, fullname, path, target=None):
        """Finds the spec for a tako module if it exists."""
        dot = '.'
        spec = None
        path = sys.path if path is None else path
        if dot not in fullname and dot not in path:
            path = [dot] + path
        name = fullname.rsplit(dot, 1)[-1]
        fname = name + '.tako'
        for p in path:
            if not isinstance(p, str):
                continue
            if not os.path.isdir(p) or not os.access(p, os.R_OK):
                continue
            if fname not in (x.name for x in scandir(p)):
                continue
            spec = ModuleSpec(fullname, self)
            self._filenames[fullname] = os.path.join(p, fname)
            break
        return spec

    #
    # SourceLoader methods
    #
    def get_filename(self, fullname):
        """Returns the filename for a module's fullname."""
        return self._filenames[fullname]

    def get_data(self, path):
        """Gets the bytes for a path."""
        raise NotImplementedError

    def get_code(self, fullname):
        """Gets the code object for a tako file."""
        filename = self._filenames.get(fullname, None)
        if filename is None:
            msg = "tako file {0!r} could not be found".format(fullname)
            raise ImportError(msg)
        with open(filename, 'r') as f:
            src = f.read()
        src = src if src.endswith('\n') else src + '\n'
        execer = self.execer
        execer.filename = filename
        ctx = {}  # dummy for modules
        code = execer.compile(src, glbs=ctx, locs=ctx)
        return code


sys.meta_path.append(TakoImportHook())
