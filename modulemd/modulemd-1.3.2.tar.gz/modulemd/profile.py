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

supported_content = ( "rpms", )

class ModuleProfile(object):
    """Class representing a particular module profile."""

    def __init__(self):
        """Creates a new ModuleProfile instance."""
        self.description = ""
        self.rpms = set()

    def __repr__(self):
        return ("<ModuleProfile: "
                "description: {0}, "
                "rpms: {1}>").format(
                        repr(self.description),
                        repr(sorted(self.rpms))
                        )

    def __bool__(self):
        return True if (self.description or self.rpms) else False

    __nonzero__ = __bool__

    @property
    def description(self):
        """A string property representing a detailed description of the
        profile."""
        return self._description

    @description.setter
    def description(self, s):
        if not isinstance(s, str):
            raise TypeError("profile.description: data type not supported")
        self._description = s

    @property
    def rpms(self):
        """A set of binary RPM packages included in this profile."""
        return self._rpms

    @rpms.setter
    def rpms(self, ss):
        if not isinstance(ss, set):
            raise TypeError("profile.rpms: data type not supported")
        for v in ss:
            if not isinstance(v, str):
                raise TypeError("profile.rpms: data type not supported")
        self._rpms = ss

    def add_rpm(self, s):
        """Adds a binary RPM package to the profile set.

        :param str s: Binary RPM package name
        """
        if not isinstance(s, str):
            raise TypeError("profile.add_rpm: data type not supported")
        self._rpms.add(s)

    def del_rpm(self, s):
        """Removes the supplied package name from the profile package set.

        :param str s: Binary RPM package name
        """
        if not isinstance(s, str):
            raise TypeError("profile.del_rpm: data type not supported")
        self._rpms.discard(s)

    def clear_rpms(self):
        """Clear the profile binary RPM package set."""
        self._rpms.clear()
