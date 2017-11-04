#! /usr/bin/env python

"""Parse argparse-passed command-line arguments by commas

Copyright:
    __init.py__  parse argparse-passed command-line arguments by commas
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

import argparse

__author__ = 'Alex Hyer'
__email__ = 'theonehyer@gmail.com'
__license__ = 'GPLv3'
__maintainer__ = 'Alex Hyer'
__status__ = 'Production/Stable'
__version__ = '1.0.3'


class ParseCommas(argparse.Action):
    """Argparse Action that parses arguments by commas

    Attributes:
        option_strings (list): list of str giving command line flags that
                               call this action

        dest (str): Namespace reference to value

        nargs (str): number of args as special char or int

        **kwargs (various): optional arguments to pass to super call
    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        """Initialize class and spawn self as Base Class w/o nargs

        This class will "make" nargs by parsing the commas so it only accepts
        a single string, not a list.

        Args:
            option_strings (list): list of str giving command line flags that
                                   call this action

            dest (str): Namespace reference to value

            nargs (str): number of args as special char or int

            **kwargs (various): optional arguments to pass to super call
        """

        # Only accept a single value to analyze
        if nargs is not None:
            raise ValueError('nargs not allowed for ParseCommas')

        # Call self again but without nargs
        super(ParseCommas, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        """Called by Argparse when user specifies a comma-separated list

        Simply splits a list by commas and adds the values to namespace.

        Args:
            parser (ArgumentParser): parser used to generate values

            namespace (Namespace): namespace to set values for

            value (str): actual value specified by user

            option_string (str): argument flag used to call this function

        Raises:
            TypeError: if value is not a string

            ValueError: if value cannot, for any reason, be parsed
                        by commas
        """

        # This try/except should already be taken care of by Argparse
        try:
            assert type(value) is str
        except AssertionError:
            raise TypeError('{0} is not a string'.format(value))

        try:
            arguments = filter(None, value.split(','))
        except:
            raise ValueError('{0} could not be parsed by commas'
                             .format(value))

        setattr(namespace, self.dest, arguments)
