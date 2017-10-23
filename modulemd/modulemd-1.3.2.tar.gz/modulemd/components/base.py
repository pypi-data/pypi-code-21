# -*- coding: utf-8 -*-


# Copyright (c) 2016  Red Hat, Inc.
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

import sys

if sys.version_info > (3,):
    long = int

class ModuleComponentBase(object):
    """A base class for definining module component types."""

    def __init__(self, name, rationale, buildorder=0):
        """Creates a new ModuleComponentBase instance."""
        self.name = name
        self.rationale = rationale
        self.buildorder = buildorder

    def __repr__(self):
        return ("<ModuleComponentBase: "
                "name: {0}, "
                "rationale: {1}, "
                "buildorder: {2}>").format(
                        repr(self.name),
                        repr(self.rationale),
                        repr(self.buildorder)
                        )

    def __bool__(self):
        return True if (self.name or self.rationale or self.buildorder) else False

    __nonzero__ = __bool__

    @property
    def name(self):
        """A string property representing the component name."""
        return self._name

    @name.setter
    def name(self, s):
        if not isinstance(s, str):
            raise TypeError("componentbase.name: data type not supported")
        self._name = s

    @property
    def rationale(self):
        """A string property representing the rationale for the component
        inclusion in the module.
        """
        return self._rationale

    @rationale.setter
    def rationale(self, s):
        if not isinstance(s, str):
            raise TypeError("componentbase.rationale: data type not supported")
        self._rationale = s

    @property
    def buildorder(self):
        """An integer property representing the buildorder index for this
        component.
        """
        return self._buildorder

    @buildorder.setter
    def buildorder(self, i):
        if not isinstance(i, (int, long)):
            raise TypeError("componentbase.buildorder: data type not supported")
        self._buildorder = i
