# -*- coding: utf-8 -*-

# Copyright 2017 Nico Madysa

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Count which header is included how many times.

This script goes through a C or C++ project and searches for #include
directives. It recursively follows project header includes and prints
statistics about which header was included how many times. This
indicates which headers are depended on the most, which is useful when
debugging long compile times of medium-sized projects.
"""

import sys
import argparse
from pathlib import Path
from collections import Counter

from headercount.files import HEADER_SUFFIXES
from headercount.files import iter_input_files
from headercount.includes import get_includes_lists


def get_version():
    """Return the version of this package as a string."""
    return '1.0.0'


def prune_includes_lists(includes_lists, *, headers=False, system=False,
                         duplicates=False):
    """Remove information from the list of includes lists.

    Args:
        includes_lists: A `dict` from file `Path` to lists of
            `Include`s in that file. This `dict` is modified in-place.
        headers: Remove all header files (and their includes lists)
            from `includes_lists`.
        system: Remove all system-header includes from each list in
            `includes_lists`.
        duplicates: For each list in `includes_lists`, remove all
            duplicate `Include`s.
    """
    if headers:
        files = list(includes_lists.keys())
        for file_ in files:
            if file_.suffix in HEADER_SUFFIXES:
                del includes_lists[file_]
    if system or duplicates:
        for includes in includes_lists.values():
            filtered = includes
            if duplicates:
                filtered = set(filtered)
            if system:
                filtered = (include for include in filtered
                            if not include.is_system())
            includes[:] = filtered


def get_parser():
    """Return an argparse.ArgumentParser instance."""
    description, _, epilog = __doc__.partition("\n")
    parser = argparse.ArgumentParser(description=description,
                                     epilog=epilog)
    inctrl = parser.add_argument_group('input control')
    inctrl.add_argument('-r', '--recursive', action='store_true',
                        help='Recursively search directories for C/C++ '
                        'files.')
    inctrl.add_argument('--exclude', type=str, action='append', default=[],
                        metavar='PATTERN', help='Skip any file whose '
                        'name matches %(metavar)s.')
    inctrl.add_argument('--exclude-dir', type=str, action='append', default=[],
                        metavar='PATTERN', help='If -r is passed, do '
                        'not recurse into directories whose name '
                        'matches %(metavar)s. If -r is not passed, '
                        'this does not do anything.')
    parser.add_argument('infiles', type=str, nargs='+', metavar='FILE',
                        help='A file to search for include files. If '
                        '%(metavar)s does not have the suffix of a '
                        'C/C++ file, it is ignored. If -r is passed, '
                        'this may also be a directory to search for '
                        'C/C++ files.')
    parser.add_argument('-S', '--no-system', action='store_true',
                        help='System-header includes do not count '
                        'towards the final tally. System-header '
                        'includes are those that use angle brackets '
                        '(<...>) instead of double quotes.')
    parser.add_argument('-H', '--no-headers', action='store_true',
                        help='Header files do not count towards the '
                        'final tally. They are, however, still used to '
                        'find indirect includes.')
    parser.add_argument('-d', '--direct-only', action='store_true',
                        help='Do not search for indirectly included '
                        'files. Just count the number of #include '
                        'directives.')
    parser.add_argument('--allow-duplicates', action='store_true',
                        help='If a file is included multiple times '
                        '(literally or due to indirect includes), '
                        'count all occurrences. The default is to '
                        'assume that each file can each other file at '
                        'most once.')
    return parser


def main(argv):
    """Main function. You should pass `sys.argv[1:]` as argument."""
    args = get_parser().parse_args(argv)
    # Build the list of files that are to be searched.
    infiles = iter_input_files(
        args.infiles,
        recursive=args.recursive,
        exclude=args.exclude,
        exclude_dir=args.exclude_dir
        )
    # Search each file for a list of included files -- either
    # direct+indirect includes or direct includes only.
    includes_lists = get_includes_lists(
        infiles,
        inclusive=not args.direct_only,
        )
    prune_includes_lists(
        includes_lists,
        system=args.no_system,
        headers=args.no_headers,
        duplicates=not args.allow_duplicates,
        )
    # Turn the lists into counters. Note: If we removed duplicates in
    # the step above, all counters will be `1` at max.
    counters = (Counter(includes) for includes in includes_lists.values())
    # Put the counters together. This is where we get the actual
    # statistics!
    total_count = sum(counters, Counter())
    # Print to stdout.
    for (filename, count) in total_count.most_common():
        print(count, filename)
