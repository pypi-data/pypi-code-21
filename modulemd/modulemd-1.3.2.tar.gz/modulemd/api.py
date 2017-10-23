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

class ModuleAPI(object):
    """Class representing a particular module API."""

    def __init__(self):
        """Creates a new ModuleAPI instance."""
        self.rpms = set()

    def __repr__(self):
        return ("<ModuleAPI: "
                "rpms: {0}>").format(
                        repr(sorted(self.rpms))
                        )

    def __bool__(self):
        return True if self.rpms else False

    __nonzero__ = __bool__

    @property
    def rpms(self):
        """A set of binary RPM packages defining this module's API."""
        return self._rpms

    @rpms.setter
    def rpms(self, ss):
        if not isinstance(ss, set):
            raise TypeError("api.rpms: data type not supported")
        for v in ss:
            if not isinstance(v, str):
                raise TypeError("api.rpms: data type not supported")
        self._rpms = ss

    def add_rpm(self, s):
        """Adds a binary RPM package to the API set.

        :param str s: Binary RPM package name
        """
        if not isinstance(s, str):
            raise TypeError("api.add_rpm: data type not supported")
        self._rpms.add(s)

    def del_rpm(self, s):
        """Removes the supplied package name from the API package set.

        :param str s: Binary RPM package name
        """
        if not isinstance(s, str):
            raise TypeError("api.del_rpm: data type not supported")
        self._rpms.discard(s)

    def clear_rpms(self):
        """Clear the API binary RPM package set."""
        self._rpms.clear()
