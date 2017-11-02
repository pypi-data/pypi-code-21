# -*- coding: utf-8 -*-

# Mathmaker Lib offers lualatex-printable mathematical objects.
# Copyright 2006-2017 Nicolas Hainaux <nh.techn@gmail.com>

# This file is part of Mathmaker Lib.

# Mathmaker Lib is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.

# Mathmaker Lib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Mathmaker Lib; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from abc import ABCMeta, abstractmethod


class Substitutable(object, metaclass=ABCMeta):
    """
    Any object whose Letters can be substituted by numbers.

    Any Substitutable must define a content property, should include an
    optional subst_dict argument in its __init__() method and must ensure
    that a _subst_dict is defined (an easy way to do this is calling
    Substitutable.__init__(self, subst_dict=subst_dict).
    The substitute() method may be redefined by some Substitutable objects.
    """
    def __init__(self, subst_dict=None):
        self._subst_dict = None
        if subst_dict is not None:
            self.subst_dict = subst_dict

    @property
    @abstractmethod
    def content(self):
        """The content to be substituted (list containing literal objects)."""

    @property
    def subst_dict(self):
        """Get the default dictionary to use for substitution."""
        return self._subst_dict

    @subst_dict.setter
    def subst_dict(self, sd):
        """Set the default dictionary to use for substitution."""
        if not isinstance(sd, dict):
            raise TypeError('sdict should be a dictionnary')

        if not check_lexicon_for_substitution(self.content, sd,
                                              'at_least_one'):
            raise ValueError('dictionary sd should match the Letters '
                             'of the objects list')
        self._subst_dict = sd

    def substitute(self, sd=None):
        """
        If a subst_dict has been defined, it is used for Letters substitution.
        """
        d = self.subst_dict
        if sd is not None:
            d = sd
        if d is not None:
            for elt in self.content:
                elt.substitute(d)
            return self
        else:
            raise RuntimeError('No dictionary has been provided '
                               'to perform substitution')
