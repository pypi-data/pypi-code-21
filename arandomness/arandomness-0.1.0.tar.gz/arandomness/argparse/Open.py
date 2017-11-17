#! /usr/bin/env python

"""Detects and opens compressed files for reading or writing

Copyright:
    open.py  detects and opens compressed files for reading and writing
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
from importlib import import_module
from inspect import getfullargspec
from os import linesep
from warnings import warn


__author__ = 'Alex Hyer'
__credit__ = 'Lauritz V. Thaulow'
__email__ = 'theonehyer@gmail.com'
__license__ = 'GPLv3'
__maintainer__ = 'Alex Hyer'
__status__ = 'Production/Stable'
__version__ = '1.0.0'


class Open(argparse.Action):
    """Argparse Action that detects and opens compressed files for rw

    Attributes:
        option_strings (list): list of str giving command line flags that
                               call this action

        dest (str): Namespace reference to value

        mode (str): mode to pass to (de)compression algorithm

        nargs (bool): True if multiple arguments specified

        **kwargs (various): optional arguments to pass to argparse and algo
    """

    def __init__(self, option_strings, dest, mode='rb', nargs=None, **kwargs):
        """Initialize class and spawn self as Base Class w/o nargs

        Warns:
            ImportError: if Open cannot import a compression library,
                         it warns the user that it cannot open the
                         corresponding file type

        Raises:
            ValueError: if nargs is not None, Open does not accept nargs
        """

        # Only accept a single value to analyze
        if nargs is not None:
            raise ValueError('nargs not allowed for Open')

        # Call self again but without nargs
        super(Open, self).__init__(option_strings, dest)

        # Store and establish variables used in __call__
        self.kwargs = kwargs
        self.mode = mode.lower().strip()
        self.modules = {}

        modules_to_import = {
            'bz2': 'BZ2File',
            'gzip': 'GzipFile',
            'lzma': 'LZMAFile'
        }

        # Dynamically import compression libraries and warn about failures
        for mod, _class in modules_to_import.items():
            try:
                self.modules[_class] = getattr(import_module(mod), _class)
            except (ImportError, AttributeError) as e:
                self.modules[_class] = open
                warn('Cannot process {0} files due to following error:'
                     '{1}{2}{1}You will need to install the {0} library to '
                     'properly use these files. Currently, such files will '
                     'open in text mode.'.format(mod, linesep, e))

    # Credits: https://stackoverflow.com/questions/13044562/
    # python-mechanism-to-identify-compressed-file-type-and-uncompress
    def __call__(self, parser, namespace, value, option_string=None, **kwargs):
        """Detects and opens compressed files

        Args:
            parser (ArgumentParser): parser used to generate values

            namespace (Namespace): namespace to set values for

            value (str): actual value specified by user

            option_string (str): argument flag used to call this function

            **kwargs (various): optional arguments later passed to the
                                compression algorithm
        """

        filename = value  # For readability

        algo = open  # Default to plaintext

        # Capture any mode that isn't read, such as write or append
        if self.mode.lstrip('U')[0] != 'r':

            algo_map = {
                'bz2': self.modules['BZ2File'],
                'gz':  self.modules['GzipFile'],
                'xz':  self.modules['LZMAFile']
            }

            # Base compression algorithm on file extension
            ext = value.split('.')[-1]
            try:
                algo = algo_map[ext]
            except KeyError:
                pass

        # Basically read mode
        else:

            file_sigs = {
                b'\x42\x5a\x68': self.modules['BZ2File'],
                b'\x1f\x8b\x08': self.modules['GzipFile'],
                b'\xfd7zXZ\x00': self.modules['LZMAFile']
                }

            max_len = max(len(x) for x in file_sigs.keys())

            # Check beginning of file for signature
            with open(filename, 'rb') as in_handle:
                start = in_handle.read(max_len)
                for sig in file_sigs.keys():
                    if start.startswith(sig):
                        algo = file_sigs[sig]
                        break

        # Filter all **kwargs by the args accepted by the compression algo
        algo_args = set(getfullargspec(algo).args)
        good_args = set(self.kwargs.keys()).intersection(algo_args)
        _kwargs = {arg: self.kwargs[arg] for arg in good_args}

        # Open the file using parameters defined above and store in namespace
        handle = algo(value, mode=self.mode, **_kwargs)
        setattr(namespace, self.dest, handle)
