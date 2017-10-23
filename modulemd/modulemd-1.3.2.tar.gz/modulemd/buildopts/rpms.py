# -*- coding: utf-8 -*-


# Copyright (c) 2016, 2017  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Petr Šabata <contyk@redhat.com>

from modulemd.buildopts.base import ModuleBuildoptsBase

class ModuleBuildoptsRPMs(ModuleBuildoptsBase):
    """A buildopts class for handling RPM content build options."""

    def __init__(self, macros=""):
        """Creates a new ModuleBuildoptsRPMs instance."""
        super(ModuleBuildoptsRPMs, self).__init__()
        self.macros = macros

    def __repr__(self):
        return ("<ModuleBuildoptsRPMs: "
                "macros: {0}>").format(
                        repr(self.macros)
                        )

    def __bool__(self):
        return True if self.macros else False

    __nonzero__ = __bool__

    @property
    def macros(self):
        """A string property representing the additional RPM macros that
        should be used for this module build.
        """
        return self._macros

    @macros.setter
    def macros(self, s):
        if not isinstance(s, str):
            raise TypeError("buildoptsrpm.macros: data type not supported")
        self._macros = s
