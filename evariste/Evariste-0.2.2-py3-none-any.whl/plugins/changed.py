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

"""Plugin to evaluate and store modification times of files.

It is used not to re-compile files that have not changed.
"""

from datetime import datetime
import os
import pathlib

from evariste import plugins
from evariste.hooks import ContextHook
from evariste.tree import File

class MakeArchive(ContextHook):
    """Hook called before and after archive creation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree = None

    def enter(self, tree, *__args, **__kwargs):
        self.tree = tree

    def exit(self, value=None):
        if self.plugin.compile(self.tree):
            self.local.tree[self.tree.from_source]['archivepath'] = value
        return value

class BuildTreeItem(ContextHook):
    """Hook called before and after the tree is built."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree = None

    def enter(self, tree, *__args, **__kwargs):
        self.tree = tree

    def exit(self, value=None):
        """Compare data with cache to see if a compilation is needed."""
        if not isinstance(self.tree, File):
            return value

        tree = self.tree

        # If the --always-compile argument was given to the command line call,
        # do compile.
        if self.shared.setup['arguments']['always_compile']:
            self.plugin.files_to_compile.add(tree.from_fs.resolve())
            return value

        # If tree is not in hash, compile it
        if (self.local.tree[tree.from_source] is None) or (self.local.tree[tree.from_source] == {}):
            self.plugin.files_to_compile.add(tree.from_fs.resolve())
            return value

        # Otherwise, check if data hash has changed
        for key in ["depends", "target"]:
            dependencies = self.local.tree[tree.from_source][key]
            for depend in dependencies:
                cache_mtime = dependencies[depend][self.local.setup['time']]
                if self.local.setup['time'] == 'vcs':
                    file_mtime = tree.vcs.last_modified(pathlib.Path(depend))
                else:
                    try:
                        file_mtime = datetime.fromtimestamp(os.path.getmtime(depend))
                    except FileNotFoundError:
                        self.plugin.files_to_compile.add(tree.from_fs.resolve())
                        return value
                if cache_mtime != file_mtime:
                    self.plugin.files_to_compile.add(tree.from_fs.resolve())
                    return value

        return value

class CompileFile(ContextHook):
    """Hook called before and after compilation of one file."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree = None

    def enter(self, tree, *args, **kwargs):
        self.tree = tree

    def exit(self, value=None):
        """Store the modification time of file and its dependencies."""
        if not isinstance(self.tree, File):
            return

        tree = self.tree
        if not tree.report.success:
            self.plugin.files_to_compile.discard(tree.from_fs.resolve())
            return

        if self.local.tree[tree.from_source] is None:
            self.local.tree[tree.from_source] = dict()

        # Saving file and dependencies data into cache
        self.local.tree[tree.from_source]['depends'] = {
            file.as_posix(): {
                'vcs': tree.vcs.last_modified(file),
                'fs': datetime.fromtimestamp(os.path.getmtime(file.as_posix()))
            }
            for file
            in tree.full_depends()
            }
        self.local.tree[tree.from_source]['target'] = {
            file.as_posix(): {
                'vcs': tree.vcs.last_modified(file),
                'fs': datetime.fromtimestamp(os.path.getmtime(file.as_posix()))
            }
            for file
            in [tree.root.from_fs / tree.report.target]
            }

        # Mark dependencies as ignored (not to be compiled)
        self.plugin.files_to_ignore.update([
            depend.resolve()
            for depend
            in tree.depends()
            ])

class Changed(plugins.PluginBase):
    """Plugin to evaluate and store modification times of files."""

    plugin_type = ''
    keyword = "changed"
    default_setup = {
        'time': 'vcs',
        }
    hooks = {
        'buildtreeitem': BuildTreeItem,
        'compilefile': CompileFile,
        'makearchive': MakeArchive,
        }
    required = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.files_to_compile = set()
        self.files_to_ignore = set()

    def compile(self, tree):
        """Return `True` iff file `tree` is to be compiled.

        It is not compiled if:
        - nothing has changed since last compilation;
        - it is a dependency of a file described in previous item.
        """
        return (
            (tree.from_fs.resolve() in self.files_to_compile)
            and
            (tree.from_fs.resolve() not in self.files_to_ignore)
            )
