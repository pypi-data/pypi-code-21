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

"""Test of the plugin dependencies"""

import os

from evariste.plugins import PluginNotFound

from . import TestLoadedPlugins
from .. import disable_logging

DEPENDSDIR = os.path.join(
    os.path.dirname(__file__),
    "depends",
    )

def string2set(string):
    """Turn a string into a set of stripped non-empty lines"""
    return set([
        line.strip() for line in string.split("\n") if line.strip()
        ])

class TestDefaultSetup(TestLoadedPlugins):
    """Testing default setup"""
    # pylint: disable=too-few-public-methods

    def test_noplugins(self):
        """Test default and required plugins."""
        with self.subTest():
            self.assertSetEqual(
                self._loaded_plugins({
                    'setup': {
                        'libdirs': DEPENDSDIR,
                        },
                    }),
                set([
                    'default',
                    'required',
                    ]) | self.default_plugins
                )

        with self.subTest():
            self.assertSetEqual(
                self._loaded_plugins({
                    'setup': {
                        'libdirs': DEPENDSDIR,
                        'disable_plugins': ['default', 'goodstuff'],
                        },
                    }),
                set([
                    'required',
                    ]) | self.default_plugins
                )

    def test_disable_required(self):
        """Exception is raised when disabling required plugin."""
        with self.assertLogs("evariste", level="WARNING") as log:
            self.assertSetEqual(
                self._loaded_plugins({
                    'setup': {
                        'libdirs': DEPENDSDIR,
                        'disable_plugins': ['required', 'goodstuff', 'default'],
                        },
                    }),
                set([
                    "required",
                    ]) | self.default_plugins,
                )
            self.assertEqual(
                log.output,
                [(
                    "WARNING:evariste:Disabling plugin 'required' is "
                    "asked by setup, but it is required. Still enabling."
                    )],
                )

    def test_non_existent_plugin(self):
        """Test exception when trying to enable a non-existent plugin."""
        with self.assertRaises(PluginNotFound):
            self._loaded_plugins({
                'setup': {
                    'libdirs': DEPENDSDIR,
                    'enable_plugins': ['nonexistent'],
                    },
                })

    def test_depends_simple(self):
        """Test simple dependencies"""
        with self.subTest():
            self.assertSetEqual(
                self._loaded_plugins({
                    'setup': {
                        'libdirs': DEPENDSDIR,
                        'disable_plugins': ['default', 'goodstuff'],
                        'enable_plugins': ['dependsoptional'],
                        },
                    }),
                set([
                    'required',
                    'dependsoptional',
                    'foo',
                    ]) | self.default_plugins
                )

        with self.subTest():
            self.assertSetEqual(
                self._loaded_plugins({
                    'setup': {
                        'libdirs': DEPENDSDIR,
                        'disable_plugins': ['default', 'goodstuff', 'foo'],
                        'enable_plugins': ['dependsoptional'],
                        },
                    }),
                set([
                    'required',
                    'dependsoptional',
                    ]) | self.default_plugins
                )

        with self.subTest():
            self.assertSetEqual(
                self._loaded_plugins({
                    'setup': {
                        'libdirs': DEPENDSDIR,
                        'disable_plugins': ['default', 'goodstuff'],
                        'enable_plugins': ['dependsrequired'],
                        },
                    }),
                set([
                    'dependsrequired',
                    'foo',
                    'required',
                    ]) | self.default_plugins
                )

        with disable_logging():
            with self.subTest():
                self.assertSetEqual(
                    self._loaded_plugins({
                        'setup': {
                            'libdirs': DEPENDSDIR,
                            'disable_plugins': ['default', 'goodstuff', 'foo'],
                            'enable_plugins': ['dependsrequired'],
                            },
                        }),
                    set([
                        'dependsrequired',
                        'foo',
                        'required',
                        ]) | self.default_plugins
                    )

    def test_depends_recursive(self):
        """Test recursive dependencies"""
        with disable_logging():
            with self.subTest():
                self.assertSetEqual(
                    self._loaded_plugins({
                        'setup': {
                            'libdirs': DEPENDSDIR,
                            'disable_plugins': ['default', 'goodstuff', 'foo'],
                            'enable_plugins': ['dependsrequiredrequired'],
                            },
                        }),
                    set([
                        'dependsrequiredrequired',
                        'dependsrequired',
                        'foo',
                        'required',
                        ]) | self.default_plugins
                    )

        with self.subTest():
            self.assertSetEqual(
                self._loaded_plugins({
                    'setup': {
                        'libdirs': DEPENDSDIR,
                        'disable_plugins': ['default', 'goodstuff'],
                        'enable_plugins': ['dependsrequiredoptional'],
                        },
                    }),
                set([
                    'dependsrequiredoptional',
                    'dependsoptional',
                    'foo',
                    'required',
                    ]) | self.default_plugins
                )

        with self.subTest():
            self.assertSetEqual(
                self._loaded_plugins({
                    'setup': {
                        'libdirs': DEPENDSDIR,
                        'disable_plugins': ['default', 'goodstuff', 'foo'],
                        'enable_plugins': ['dependsrequiredoptional'],
                        },
                    }),
                set([
                    'dependsrequiredoptional',
                    'dependsoptional',
                    'required',
                    ]) | self.default_plugins
                )

        with self.subTest():
            self.assertSetEqual(
                self._loaded_plugins({
                    'setup': {
                        'libdirs': DEPENDSDIR,
                        'disable_plugins': ['default', 'goodstuff'],
                        'enable_plugins': ['dependsoptionalrequired'],
                        },
                    }),
                set([
                    'dependsoptionalrequired',
                    'dependsrequired',
                    'foo',
                    'required',
                    ]) | self.default_plugins
                )

        with self.subTest():
            self.assertSetEqual(
                self._loaded_plugins({
                    'setup': {
                        'libdirs': DEPENDSDIR,
                        'disable_plugins': ['default', 'goodstuff', 'dependsrequired'],
                        'enable_plugins': ['dependsoptionalrequired'],
                        },
                    }),
                set([
                    'dependsoptionalrequired',
                    'required',
                    ]) | self.default_plugins
                )

        with self.subTest():
            self.assertSetEqual(
                self._loaded_plugins({
                    'setup': {
                        'libdirs': DEPENDSDIR,
                        'disable_plugins': ['default', 'goodstuff'],
                        'enable_plugins': ['dependsoptionaloptional'],
                        },
                    }),
                set([
                    'dependsoptional',
                    'dependsoptionaloptional',
                    'foo',
                    'required',
                    ]) | self.default_plugins
                )

        with self.subTest():
            self.assertSetEqual(
                self._loaded_plugins({
                    'setup': {
                        'libdirs': DEPENDSDIR,
                        'disable_plugins': ['default', 'goodstuff', 'foo'],
                        'enable_plugins': ['dependsoptionaloptional'],
                        },
                    }),
                set([
                    'dependsoptional',
                    'dependsoptionaloptional',
                    'required',
                    ]) | self.default_plugins
                )
