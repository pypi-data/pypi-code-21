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

"""Test of the shared plugin"""

import unittest

from evariste.builder import Builder

def default_shared():
    """Return a default, as empty as possible, :class:`evariste.shared.Shared` object.
    """
    return Builder.from_setupdict(
        {
            'setup': {
                'vcs': 'vcs.none',
                'enable_plugins': ['vcs.none'],
                },
            }
        ).shared

class TestShared(unittest.TestCase):
    """Testing Shared"""
    # pylint: disable=too-few-public-methods, no-member

    def test_setup(self):
        """Test Shared.setup"""
        shared = default_shared()

        self.assertEqual(shared.setup['plugin']['foo'], None)
        shared.setup['plugin']['foo'] = 'bar'
        self.assertEqual(shared.setup['plugin']['foo'], 'bar')

        view = shared.get_plugin_view('plugin')
        self.assertEqual(view.setup['foo'], 'bar')
        self.assertEqual(view.setup['foo1'], None)
        view.setup['foo1'] = 'bar1'
        self.assertEqual(view.setup['foo1'], 'bar1')
        self.assertEqual(shared.setup['plugin']['foo1'], 'bar1')

    def test_plugin(self):
        """Test Shared.plugin"""
        shared = default_shared()

        self.assertEqual(shared.plugin['plugin1'], None)
        shared.plugin['plugin1'] = 'bar1'
        self.assertEqual(shared.plugin['plugin1'], 'bar1')

        view1 = shared.get_plugin_view('plugin1')
        view2 = shared.get_plugin_view('plugin2')
        self.assertEqual(view1.plugin, 'bar1')
        self.assertEqual(view2.plugin, None)
        view2.plugin = 'bar2'
        self.assertEqual(view2.plugin, 'bar2')
        self.assertEqual(shared.plugin['plugin2'], 'bar2')

    def test_tree(self):
        """Test Shared.tree"""
        shared = default_shared()

        self.assertEqual(shared.tree['path1']['plugin1'], None)
        shared.tree['path1']['plugin1'] = 'bar1'
        self.assertEqual(shared.tree['path1']['plugin1'], 'bar1')

        view = shared.get_tree_view('path1')
        self.assertEqual(view.tree['plugin1'], 'bar1')
        self.assertEqual(view.tree['plugin2'], None)
        view.tree['plugin2'] = 'bar2'
        self.assertEqual(view.tree['plugin2'], 'bar2')
        self.assertEqual(shared.tree['path1']['plugin2'], 'bar2')

        plugin_view = shared.get_plugin_view('plugin1')
        self.assertEqual(plugin_view.tree['path1'], 'bar1')

        tree2_view = shared.get_tree_view('path2')
        self.assertEqual(tree2_view.tree['plugin1'], None)
        self.assertEqual(plugin_view.tree['path2'], None)
        tree2_view.tree['plugin1'] = "bar"
        self.assertEqual(plugin_view.tree['path2'], "bar")
        self.assertEqual(tree2_view.tree['plugin1'], "bar")
        self.assertEqual(shared.tree['path2']['plugin1'], "bar")
