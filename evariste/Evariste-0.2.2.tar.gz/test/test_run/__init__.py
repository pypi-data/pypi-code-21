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

"""Test involving compilation"""

import collections
import difflib
import filecmp
import os
import re
import sys
import unittest

from evariste.builder import Builder
from evariste.setup import Setup

class Compare:
    """Compare some characteristics of files."""
    # pylint: disable=too-few-public-methods

    message = ""

    @staticmethod
    def compare(first, second):
        """Compare files. Return `True` iff they differ."""
        raise NotImplementedError()

class FirstOnly(Compare):
    """File is present in left directory only."""
    # pylint: disable=abstract-method, too-few-public-methods

    message = "Only in first"

class SecondOnly(Compare):
    """File is present in right directory only."""
    # pylint: disable=abstract-method, too-few-public-methods

    message = "Only in second"

class SameContent(Compare):
    """Files have same content"""
    # pylint: disable=too-few-public-methods

    message = "File content differ"

    @staticmethod
    def compare(left, right):
        result = filecmp.cmp(left, right)
        if not result:
            with open(left) as leftfile:
                with open(right) as rightfile:
                    sys.stderr.writelines(difflib.Differ().compare(
                        leftfile.readlines(),
                        rightfile.readlines(),
                        ))
        return result


class TestCompilation(unittest.TestCase):
    """Test of compilation"""

    @staticmethod
    def _run_evariste(local):
        """Create a builder, from a dummy setup file.

        Return a set a loaded plugins.
        """
        setup = Setup.from_dict({
            'setup': {
                'vcs': 'vcs.git',
                },
            'vcs': {
                'enable_plugins': ['vcs.git'],
                },
            })
        setup.update(local, extend_list=True)

        with Builder.from_setupdict(setup) as builder:
            builder.compile()
            for renderer in builder.iter_renderers():
                renderer()

    def assertTreeEqual(self, first, second, rules=None):
        """Compare if directory trees `first` and `second` are equal.

        :param list rules: List of tuples `(regexp, Compare)` objects, for
            special rules concerning objects. When comparing a file, the first
            tuple with a regexp matching the file (base) name is considered,
            and its associated `Compare` class is used to compare files. By
            default, the :class:`SameContent` class is used. This is useful to
            define custom matches (for instance, two generated PDF will not be
            exactly equal, so a fuzzy comparison may be used).
        """
        # pylint: disable=invalid-name
        if rules is None:
            rules = list()
        rules.append((r".*", SameContent))
        rules = [
            (re.compile(regexp), comparator)
            for regexp, comparator
            in rules
            ]
        errors = self.compare_dirs(first, second, rules)
        if sum([len(files) for files in errors.values()]) != 0:
            raise AssertionError(
                "\n".join([
                    "{message}:\n\t{files}".format(
                        message=error.message,
                        files="\n\t".join(errors[error])
                        )
                    for error in errors
                    ])
                )

    def compare_dirs(self, first, second, rules):
        """Compare directories, and return a dictionary of differences."""
        errors = collections.defaultdict(list)

        first_set = set(os.listdir(first))
        second_set = set(os.listdir(second))
        for filename in first_set - second_set:
            errors[FirstOnly].append(filename)
        for filename in second_set - first_set:
            errors[SecondOnly].append(filename)

        for path in first_set & second_set:
            if os.path.isdir(os.path.join(first, path)):
                for (errorname, filenames) in self.compare_dirs(
                        os.path.join(first, path),
                        os.path.join(second, path),
                        rules).items():
                    for name in filenames:
                        errors[errorname].append(os.path.join(path, name))
            else:
                for regexp, comparator in rules:
                    if regexp.match(path):
                        if not comparator.compare(
                                os.path.join(first, path),
                                os.path.join(second, path),
                            ):
                            errors[comparator].append(path)
                        break

        return errors
