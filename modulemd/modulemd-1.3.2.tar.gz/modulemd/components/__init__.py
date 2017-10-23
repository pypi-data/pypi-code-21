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

from modulemd.components.module import ModuleComponentModule
from modulemd.components.rpm import ModuleComponentRPM

supported_content = ( "rpms", "modules", )

class ModuleComponents(object):
    """Class representing components of a module."""

    def __init__(self):
        """Creates a new ModuleComponents instance."""
        self.modules = dict()
        self.rpms = dict()

    def __repr__(self):
        return ("<ModuleComponents: "
                "modules: {0}, "
                "rpms: {1}>").format(
                        repr(sorted(self.modules)),
                        repr(sorted(self.rpms))
                        )

    def __bool__(self):
        return True if self.all else False

    __nonzero__ = __bool__

    @property
    def all(self):
        """Returns all the components regardless of their content type."""
        ac = list()
        ac.extend(self.rpms.values())
        ac.extend(self.modules.values())
        return ac

    @property
    def rpms(self):
        """A dictionary of RPM components in this module.  The keys are SRPM
        names, the values ModuleComponentRPM instances.
        """
        return self._rpms

    @rpms.setter
    def rpms(self, d):
        if not isinstance(d, dict):
            raise TypeError("components.rpms: data type not supported")
        for k, v in d.items():
            if not isinstance(k, str) or not isinstance(v, ModuleComponentRPM):
                raise TypeError("components.rpms: data type not supported")
        self._rpms = d

    def add_rpm(self, name, rationale, buildorder=0,
            repository="", ref="", cache="", arches=set(), multilib=set()):
        """Adds an RPM to the set of module components."""
        component = ModuleComponentRPM(name, rationale)
        component.buildorder = buildorder
        component.repository = repository
        component.ref = ref
        component.cache = cache
        component.arches = arches
        component.multilib = multilib
        self._rpms[name] = component

    def del_rpm(self, s):
        """Removes the supplied RPM from the set of module components."""
        if not isinstance(s, str):
            raise TypeError("components.del_rpm: data type not supported")
        if s in self._rpms:
            del self._rpms[s]

    def clear_rpms(self):
        """Clear the RPM component dictionary."""
        self._rpms.clear()

    @property
    def modules(self):
        """A dictionary of module-type components in this module.  The keys are
        module names, the values ModuleComponentModule instances.
        """
        return self._modules

    @modules.setter
    def modules(self, d):
        if not isinstance(d, dict):
            raise TypeError("components.modules: data type not supported")
        for k, v in d.items():
            if not isinstance(k, str) or not isinstance(v, ModuleComponentModule):
                raise TypeError("components.modules: data type not supported")
        self._modules = d

    def add_module(self, name, rationale, buildorder=0,
            repository="", ref=""):
        component = ModuleComponentModule(name, rationale)
        component.buildorder = buildorder
        component.repository = repository
        component.ref = ref
        self._modules[name] = component

    def del_module(self, s):
        """Removes the supplied module from the set of module components."""
        if not isinstance(s, str):
            raise TypeError("components.del_module: data type not supported")
        if s in self._modules:
            del self._modules[s]

    def clear_modules(self):
        """Clear the module-type component dictionary."""
        self._modules.clear()
