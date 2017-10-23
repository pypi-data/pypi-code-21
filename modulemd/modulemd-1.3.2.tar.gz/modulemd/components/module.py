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

from modulemd.components.base import ModuleComponentBase

class ModuleComponentModule(ModuleComponentBase):
    """A component class for handling module-type content."""

    def __init__(self, name, rationale, buildorder=0,
            repository="", ref=""):
        """Creates a new ModuleComponentModule instance."""
        super(ModuleComponentModule, self).__init__(name, rationale, buildorder)
        self.repository = repository
        self.ref = ref

    def __repr__(self):
        return ("<ModuleComponentModule: "
                "name: {0}, "
                "rationale: {1}, "
                "buildorder: {2}, "
                "repository: {3}, "
                "ref: {4}>").format(
                        repr(self.name),
                        repr(self.rationale),
                        repr(self.buildorder),
                        repr(self.repository),
                        repr(self.ref)
                        )

    def __bool__(self):
        return True if (self.name or self.rationale or self.buildorder or
                self.repository or self.ref) else False

    __nonzero__ = __bool__

    @property
    def repository(self):
        """A string property representing the VCS repository with the modulemd
        file and possibly other module data.
        """
        return self._repository

    @repository.setter
    def repository(self, s):
        if not isinstance(s, str):
            raise TypeError("componentmodule.repository: data type not supported")
        self._repository = s

    @property
    def ref(self):
        """A string property representing the particular repository commit
        hash, branch or tag name used in this module.
        """
        return self._ref

    @ref.setter
    def ref(self, s):
        if not isinstance(s, str):
            raise TypeError("componentmodule.ref: data type not supported")
        self._ref = s
