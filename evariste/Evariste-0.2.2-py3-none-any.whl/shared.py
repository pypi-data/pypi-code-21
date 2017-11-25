# Copyright Louis Paternault 2015
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Share global data between evariste objects."""

from enum import Enum

from evariste.utils import DeepDict

class ViewPoint(Enum):
    """Point of view: from plugin or from tree?"""
    # pylint: disable=too-few-public-methods
    plugin = 1
    tree = 2

ATTRIBUTES = {
    'setup': [ViewPoint.plugin],
    'plugin': [ViewPoint.plugin],
    'tree': [ViewPoint.tree, ViewPoint.plugin],
    }

class SharedDeepDict(DeepDict):
    """DeepDict class, with a factory to build them as shared attributes."""

    @classmethod
    def from_attr(cls, attr, dictionary=None):
        """Default value for attribute."""
        return cls(len(ATTRIBUTES[attr]), dictionary)

class _SubSharedView:
    """View of  a shared data.

    :param str keyword: Keyword of the point of view (e.g. 'renderer.html').
    :param str attr: Object being viewed (e.g. 'setup').
    :param ViewPoint viewpoint: Point of view (tree, or plugin).
    :param Shared shared: Shared data.
        """
    # pylint: disable=too-few-public-methods

    def __init__(self, keyword, attr, viewpoint, shared):
        self.keyword = keyword
        self.viewpoint = viewpoint
        self.shared = shared
        self.attr = attr


class _SubSharedViewNoDict(_SubSharedView):
    """View of a shared data, not as a dictionary."""
    # pylint: disable=too-few-public-methods

    def __getitem__(self, key):
        return getattr(self.shared, self.attr)[key]

    def __setitem__(self, key, value):
        getattr(self.shared, self.attr)[key] = value

class _SubSharedViewDict(_SubSharedView):
    """View of a shared data, as a dictionary (of dictionaries of ...)"""
    # pylint: disable=too-few-public-methods

    def __getitem__(self, key):
        shared = getattr(self.shared, self.attr)
        for viewpoint in ATTRIBUTES[self.attr]:
            if viewpoint == self.viewpoint:
                shared = shared[self.keyword]
            else:
                shared = shared[key]
        return shared

    def __setitem__(self, key, value):
        shared = getattr(self.shared, self.attr)
        for viewpoint in ATTRIBUTES[self.attr][:-1]:
            if viewpoint == self.viewpoint:
                shared = shared[self.keyword]
            else:
                shared = shared[key]
        if ATTRIBUTES[self.attr][-1] == self.viewpoint:
            shared[self.keyword] = value
        else:
            shared[key] = value

class _MetaSharedView(type):
    """Metaclass that creates attributes corresponding to :data:`ATTRIBUTES`.
    """
    def __new__(mcs, *args, **kwargs):
        obj = super().__new__(mcs, *args, **kwargs)
        for attr in ATTRIBUTES:
            setattr(obj, attr, property(
                fget=obj.getter(attr),
                fset=obj.setter(attr),
                ))

        return obj

class _SharedView(metaclass=_MetaSharedView):
    """View of shared data, from a certain point of view."""
    # pylint: disable=too-few-public-methods

    def __init__(self, viewpoint, keyword, shared):
        self.shared = shared
        self.keyword = keyword
        self.viewpoint = viewpoint
        self.views = {}
        for attr in ATTRIBUTES:
            if viewpoint in ATTRIBUTES[attr]:
                if len(ATTRIBUTES[attr]) == 1:
                    self.views[attr] = _SubSharedViewNoDict(keyword, attr, viewpoint, shared)
                else:
                    self.views[attr] = _SubSharedViewDict(keyword, attr, viewpoint, shared)

    @classmethod
    def getter(cls, attr):
        """Returns a getter for this attribute of this point of view."""
        def getter(self):
            """Getter"""
            if isinstance(self.views[attr], _SubSharedViewNoDict):
                return self.views[attr][self.keyword]
            else:
                return self.views[attr]
        return getter

    @classmethod
    def setter(cls, attr):
        """Returns a setter for this attribute of this point of view."""
        def setter(self, value):
            """Setter"""
            if isinstance(self.views[attr], _SubSharedViewNoDict):
                self.views[attr][self.keyword] = value
            else:
                # Should not be that difficult to implement, but I do not need
                # it right now.
                raise NotImplementedError
        return setter

class Shared:
    """Shared data"""

    def __init__(self, builder, **kwargs):
        self.builder = builder
        for attr in ATTRIBUTES:
            if attr in kwargs:
                setattr(self, attr, kwargs[attr])
            else:
                setattr(self, attr, SharedDeepDict.from_attr(attr))

    def get_plugin_view(self, keyword):
        """Get this data, from the point of view of a plugin."""
        return _SharedView(ViewPoint.plugin, keyword, self)

    def get_tree_view(self, path):
        """Get this data, from the point of view of a tree."""
        return _SharedView(ViewPoint.tree, path, self)
