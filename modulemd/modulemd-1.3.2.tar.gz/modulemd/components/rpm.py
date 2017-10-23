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

class ModuleComponentRPM(ModuleComponentBase):
    """A component class for handling RPM content."""

    def __init__(self, name, rationale, buildorder=0,
            repository="", ref="", cache="", arches=set(), multilib=set()):
        """Creates a new ModuleComponentRPM instance."""
        super(ModuleComponentRPM, self).__init__(name, rationale, buildorder)
        self.repository = repository
        self.ref = ref
        self.cache = cache
        self.arches = arches
        self.multilib = multilib

    def __repr__(self):
        return ("<ModuleComponentRPM: "
                "name: {0}, "
                "rationale: {1}, "
                "buildorder: {2}, "
                "repository: {3}, "
                "ref: {4}, "
                "cache: {5}, "
                "arches: {6}, "
                "multilib: {7}>").format(
                        repr(self.name),
                        repr(self.rationale),
                        repr(self.buildorder),
                        repr(self.repository),
                        repr(self.ref),
                        repr(self.cache),
                        repr(sorted(self.arches)),
                        repr(sorted(self.multilib))
                        )

    def __bool__(self):
        return True if (self.name or self.rationale or self.buildorder or
                self.repository or self.ref or self.cache or self.arches or
                self.multilib) else False

    __nonzero__ = __bool__

    @property
    def repository(self):
        """A string property representing the VCS repository with the RPM SPEC
        file, patches and other package data.
        """
        return self._repository

    @repository.setter
    def repository(self, s):
        if not isinstance(s, str):
            raise TypeError("componentrpm.repository: data type not supported")
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
            raise TypeError("componentrpm.ref: data type not supported")
        self._ref = s

    @property
    def cache(self):
        """A string property representing the URL to the lookaside cache where
        this packages' sources are stored.
        """
        return self._cache

    @cache.setter
    def cache(self, s):
        if not isinstance(s, str):
            raise TypeError("componentrpm.cache: data type not supported")
        self._cache = s

    @property
    def arches(self):
        """A set of architectures this RPM package should be available on.  An
        empty set equals to the package being available on all supported
        architectures.
        """
        return self._arches

    @arches.setter
    def arches(self, ss):
        if not isinstance(ss, set):
            raise TypeError("componentrpm.arches: data type not supported")
        for v in ss:
            if not isinstance(v, str):
                raise TypeError("componentrpm.arches: data type not supported")
        self._arches = ss

    @property
    def multilib(self):
        """A set of architectures this package is available as multilib on.
        What this actually means varies from architecture to architecture.  An
        empty set is equal to no multilib.
        """
        return self._multilib

    @multilib.setter
    def multilib(self, ss):
        if not isinstance(ss, set):
            raise TypeError("componentrpm.multilib: data type not supported")
        for v in ss:
            if not isinstance(v, str):
                raise TypeError("componentrpm.multilib: data type not supported")
        self._multilib = ss
