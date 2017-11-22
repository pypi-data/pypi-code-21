"""
Legalese
--------
Copyright (c) 2015, 2016 Genome Research Ltd.

Authors:
* Colin Nolan <cn13@sanger.ac.uk>
* Irina Colgiu <ic4@sanger.ac.uk>

This file is part of HGI's common Python library

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
from abc import ABCMeta
from enum import Enum, unique
from typing import Generic, TypeVar, Set

from hgicommon.enums import ComparisonOperator


class Model(metaclass=ABCMeta):
    """
    Superclass that POPOs (Plain Old Python Objects) can implement.
    """
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        for property_name, value in vars(self).items():
            if other.__dict__[property_name] != self.__dict__[property_name]:
                return False
        return True

    def __str__(self) -> str:
        string_builder = []
        for property, value in vars(self).items():
            if isinstance(value, Set):
                value = str(sorted(value, key=id))
            string_builder.append("%s: %s" % (property, value))
        string_builder = sorted(string_builder)
        return "{ %s }" % ', '.join(string_builder)

    def __repr__(self) -> str:
        return "<%s object at %s: %s>" % (type(self), id(self), str(self))

    def __hash__(self):
        return hash(str(self))


class SearchCriterion(Model):
    """
    Model of an attribute search criterion.
    """
    def __init__(self, attribute: str, value: str, comparison_operator: ComparisonOperator=ComparisonOperator.EQUALS):
        self.attribute = attribute
        self.value = value
        self.comparison_operator = comparison_operator


# The type of the object that is registered
_RegistrationTarget = TypeVar("RegistrationTarget")


class RegistrationEvent(Generic[_RegistrationTarget], Model):
    """
    A model of a registration update.
    """
    @unique
    class Type(Enum):
        """
        The type of event.
        """
        REGISTERED = 0
        UNREGISTERED = 1

    def __init__(self, target: _RegistrationTarget, event_type: Type):
        """
        Constructor.
        :param target: the object the event refers to
        :param event_type: the type of update event
        """
        self.target = target
        self.event_type = event_type
