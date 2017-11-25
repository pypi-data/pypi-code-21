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

"""Test of the ``libdirs`` setup option"""

import os

from evariste.plugins import PluginNotFound

from . import TestLoadedPlugins

def absdir(path):
    """Return the absolute path of the argument (relative to this file)."""
    return os.path.join(
        os.path.dirname(__file__),
        "libdirs",
        path,
        )

class TestLibdirs(TestLoadedPlugins):
    """Testing setup `libdirs` options"""
    # pylint: disable=too-few-public-methods

    def test_nolibdirs(self):
        """Test compilation without the libdirs option"""
        self.assertSetEqual(
            self._loaded_plugins({}),
            self.default_plugins,
            )

    def test_fail(self):
        """Test failure (plugin not found)."""
        with self.assertRaises(PluginNotFound):
            self._loaded_plugins({
                'setup': {
                    'libdirs': absdir("plugins"),
                    'enable_plugins': ["foo", "bar"],
                    },
                })

    def test_libdirs(self):
        """Test compilation with the libdirs option"""
        with self.subTest("Without spaces"):
            self.assertSetEqual(
                self._loaded_plugins({
                    'setup': {
                        'libdirs': absdir("plugins"),
                        'enable_plugins': ['foo'],
                        },
                    }),
                set([
                    'foo',
                    ]) | self.default_plugins
                )

        with self.subTest("With spaces"):
            self.assertSetEqual(
                self._loaded_plugins({
                    'setup': {
                        'libdirs': '"{}"'.format(absdir("plug ins")),
                        'enable_plugins': ['bar'],
                        },
                    }),
                set([
                    "bar",
                    ]) | self.default_plugins
                )

        with self.subTest("With and without spaces"):
            self.assertSetEqual(
                self._loaded_plugins({
                    'setup': {
                        'libdirs': '{} {}'.format(
                            absdir(r"plug\ ins"),
                            absdir("plugins"),
                            ),
                        'enable_plugins': ["foo", "bar"],
                        },
                    }),
                set([
                    "bar",
                    "foo",
                    ]) | self.default_plugins
                )
