#! /usr/bin/env python

"""A many-to-many tree with self-aware features

Copyright:
    omnitree.py  A many-to-many tree with self-aware features
    Copyright (C) 2017  Alex Hyer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = 'Alex Hyer'
__email__ = 'theonehyer@gmail.com'
__license__ = 'GPLv3'
__maintainer__ = 'Alex Hyer'
__status__ = 'Inactive'
__version__ = '0.1.0a7'


class OmniTree(object):
    """A many-to-many tree for organizing and manipulating hierarchical data

    Attributes:
        label (unicode): optional, arbitrary name for node
    """

    def __init__(self, label=None, children=None, parents=None):
        """Initialize node and inform connected nodes"""

        self._children = []  # list of child nodes
        self._parents = []  # list of parent nodes
        self.label = label

        # Assign children and notify them if needed
        if children is not None:
            self._children = children
            for child in self._children:
                child.add_parents([self])

        # Assign parents and notify them if needed
        if parents is not None:
            self._parents = parents
            for parent in self._parents:
                parent.add_children([self])

    def add_children(self, children):
        """Adds new children nodes after filtering for duplicates

        Args:
            children (list): list of OmniTree nodes to add as children
        """

        self._children += [c for c in children if c not in self._children]

    def add_parents(self, parents):
        """Adds new parent nodes after filtering for duplicates

        Args:
            parents (list): list of OmniTree nodes to add as parents
        """

        self._parents += [p for p in parents if p not in self._parents]

    def find_loops(self, _path=None):
        """Crappy function that finds a single loop in the tree"""

        if _path is None:
            _path = []

        if self in _path:
            return _path + [self]
        elif self._children == []:
            return None
        else:
            for child in self._children:
                return child.find_loops(_path + [self])

    def find_branches(self, labels=False, unique=False):
        """Recursively constructs a list of pointers of the tree's structure

        Args:
            labels (bool): If True, returned lists consist of node labels.
                           If False (default), lists consist of node
                           pointers. This option is mostly intended for
                           debugging purposes.

            unique (bool): If True, return lists of all unique, linear branches
                           of the tree. More accurately, it returns a list
                           of lists where each list contains a single,
                           unique, linear path from the calling node to the
                           tree's leaf nodes. If False (default),
                           a highly-nested list is returned where each nested
                           list represents a branch point in the tree.
                           See Examples for more.

        Examples:
            >>> from arandomness.trees import OmniTree
            >>> a = OmniTree(label='a')
            >>> b = OmniTree(label='b', parents=[a])
            >>> c = OmniTree(label='c', parents=[b])
            >>> d = OmniTree(label='d', parents=[b])
            >>> e = OmniTree(label='e', parents=[c, d])
            >>> a.find_branches(labels=True)
            ['a', ['b', ['c', ['e']], ['d', ['e']]]]
            >>> a.find_branches(labels=True, unique=True)
            [['a', 'b', 'c', 'e'], ['a', 'b', 'd', 'e']]
        """

        branches = []

        # Assign proper item, pointer or label, to return
        if labels is True:
            identifier = [self.label]
        else:
            identifier = [self]

        if self._children == []:  # Base Case: current node is a leaf/end node
            return identifier

        else:  # Recursive Case: all other nodes
            for child in self._children:
                if unique is True:
                    for branch in child.find_branches(labels=labels,
                                                      unique=True):
                        # I don't know why this 'if' is necessary, but it is
                        if type(branch) is not list:
                            branch = list(branch)
                        branches.append(identifier + branch)
                else:
                    branches.append(child.find_branches(labels=labels))

            # Proper construction of list depends on 'unique'
            if unique is True:
                return branches
            else:
                return identifier + branches
