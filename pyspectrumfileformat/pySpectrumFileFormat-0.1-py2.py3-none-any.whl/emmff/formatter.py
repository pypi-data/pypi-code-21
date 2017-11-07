#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
================================================================================
:mod:`formatter` -- Parse values from XML string
================================================================================

.. module:: formatter
   :synopsis: Parse values from XML string

.. moduleauthor:: Philippe T. Pinard <philippe.pinard@gmail.com>

"""

###############################################################################
# Copyright 2010 Philippe T. Pinard
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###############################################################################

# Standard library modules.
import numbers

# Third party modules.

# Local modules.

# Project modules.

# Globals and constants variables.

class NoMatch(Exception):
    pass

class _Condition:
    def __str__(self):
        return self.__class__.__name__

    def __eq__(self, other):
        return self.__class__.__name__ == other.__class__.__name__

    def __ne__(self, other):
        return not self == other

    def from_string(self, value):
        raise NoMatch

    def to_string(self, value):
        raise NoMatch

class TrueFalseCondition(_Condition):
    def from_string(self, value):
        trues = ['true', 'yes']
        falses = ['false', 'no']

        tmpvalue = value.strip().lower()

        if tmpvalue in trues:
            return True
        elif tmpvalue in falses:
            return False
        else:
            raise NoMatch

    def to_string(self, value):
        if isinstance(value, bool):
            if value:
                return "true"
            else:
                return "false"
        else:
            raise NoMatch

class NoneCondition(_Condition):
    def from_string(self, value):
        if value.strip().lower() == 'none':
            return None
        else:
            raise NoMatch

    def to_string(self, value):
        if isinstance(value, type(None)):
            return "none"
        else:
            raise NoMatch

class NumberCondition(_Condition):
    def from_string(self, value):
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                try:
                    value = complex(value)
                except ValueError:
                    raise NoMatch

        return value

    def to_string(self, value):
        if isinstance(value, numbers.Number) and not isinstance(value, bool):
            return str(value)
        else:
            raise NoMatch

class Formatter:
    def __init__(self):
        self._conditions = []

    def register(self, condition):
        if not condition in self._conditions:
            self._conditions.append(condition)

    def deregister(self, condition):
        if condition in self._conditions:
            self._conditions.pop(condition)
        else:
            raise ValueError("Condition (%s) is not registered.")

    def _run(self, value, meth):
        matches = []

        # Loop through the condition
        for condition in self._conditions:
            try:
                result = getattr(condition, meth)(value)
            except NoMatch:
                continue

            matches.append((str(condition), result))

        if not matches:
            return value
        elif len(matches) > 1:
            error = "Found multiple formatting matches for value (%s)\n" % value
            for condition, result in matches:
                error += "- %s (%s)\n" % (result, condition)
            raise ValueError(error)
        else:
            return matches[0][1]

    def from_string(self, value):
        return self._run(value, "from_string")

    def to_string(self, value):
        return self._run(value, "to_string")

formatter = Formatter()
formatter.register(TrueFalseCondition())
formatter.register(NoneCondition())
formatter.register(NumberCondition())
