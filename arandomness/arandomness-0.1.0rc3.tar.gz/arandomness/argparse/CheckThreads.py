#! /usr/bin/env python

"""Ensures that user doesn't specify more threads than system has available

Copyright:
    CheckThreads.py  ensure threads requested does not specify system threads
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
from multiprocessing import cpu_count

__author__ = 'Alex Hyer'
__email__ = 'theonehyer@gmail.com'
__license__ = 'GPLv3'
__maintainer__ = 'Alex Hyer'
__status__ = 'Production/Stable'
__version__ = '1.0.3'


class CheckThreads(argparse.Action):
    """Argparse Action that ensures number of threads requested is valid"""

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        """Initialize class and spawn self as Base Class w/o nargs

        Args:
            option_strings (list): list of str giving command line flags that
                                   call this action

            dest (str): Namespace reference to value

            nargs (str): number of args as special char or int

            **kwargs (various): optional arguments to pass to super call
        """

        # Only accept a single value to analyze
        if nargs is not None:
            raise ValueError('nargs not allowed for ThreadCheck')

        # Call self again but without nargs
        super(CheckThreads, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        """Called by Argparse when user specifies multiple threads

        Simply asserts that the number of threads requested is greater than 0
        but not greater than the maximum number of threads the computer
        can support.

        Args:
            parser (ArgumentParser): parser used to generate values

            namespace (Namespace): parse_args() generated namespace

            values (int): actual value specified by user

            option_string (str): argument flag used to call this function

        Raises:
            TypeError: if threads is not an integer

            ValueError: if threads is less than one or greater than number of
                        threads available on computer
        """

        threads = values  # Renamed for readability

        # This try/except should already be taken care of by Argparse
        try:
            assert type(threads) is int
        except AssertionError:
            raise TypeError('{0} is not an integer'.format(str(threads)))

        try:
            assert threads >= 1
        except AssertionError:
            raise ValueError('Must use at least one thread')

        try:
            assert threads <= cpu_count()
        except AssertionError:
            raise ValueError('Cannot use more threads than available: {0}'
                             .format(str(cpu_count())))

        setattr(namespace, self.dest, threads)
