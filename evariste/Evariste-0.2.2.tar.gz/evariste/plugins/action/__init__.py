# Copyright Louis Paternault 2017
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

"""Actions performed to compile files."""

import io
import logging
import os

from evariste import errors, plugins
from evariste.hooks import ContextHook

LOGGER = logging.getLogger(__name__)

################################################################################
# Cache log

class CacheLogHook(ContextHook):
    """Hook called before and after compilation of one file."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree = None

    def enter(self, tree, *_args, **_kwargs):
        self.tree = tree

    def exit(self):
        """Store the log in cache."""
        tree = self.tree

        # Saving log into cache
        self.local.tree[tree.from_source] = tree.report.log.getvalue()

class CacheLog(plugins.PluginBase):
    """Plugin to cache compilation log."""
    # pylint: disable=too-few-public-methods

    plugin_type = ''
    keyword = "cachelog"
    hooks = {
        'compilefile': CacheLogHook,
        }

################################################################################
# Actions

class PathCompiler:
    """Compiler of one path.

    The main difference between this object and :class:`Action` is that:
        - there is one instance of :class:`Action` for the whole tree;
        - there is one instance of :class:`PathCompiler` per path.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, parent, path, keyword, shared):
        self.shared = shared
        self.keyword = keyword
        self.path = path
        self.parent = parent

    def compile(self):
        """Perform actual compilation of `self.path`."""
        raise NotImplementedError()

class Action(plugins.PluginBase):
    """Generic action"""
    # pylint: disable=too-many-instance-attributes, too-few-public-methods

    plugin_type = "action"
    pathcompiler = PathCompiler

    def compile(self, path):
        """Compile ``path``, catching :class:`EvaristeError` exceptions.

        This function *must* be thread-safe.
        """
        try:
            return self.pathcompiler(self, path, self.keyword, self.shared).compile()
        except errors.EvaristeError as error:
            LOGGER.error(str(error))
            return Report(
                path,
                success=False,
                log=io.StringIO(str(error)),
                )

class DirectoryCompiler(PathCompiler):
    """Compiler of a directory."""

    def compile(self):
        if self.success:
            log = ""
        else:
            log = "At least one file in this directory failed."
        return Report(
            self.path,
            success=self.success(),
            log=log,
            target=None,
            )

    def success(self):
        """Return ``True`` if compilation of all subpath succeeded."""
        for sub in self.path:
            if not self.path[sub].report.success:
                return False
        return True


class DirectoryAction(Action):
    """Fake action on directories."""
    # pylint: disable=abstract-method, too-few-public-methods

    keyword = "action.directory"
    pathcompiler = DirectoryCompiler
    required = True

    def match(self, dummy):
        return False

################################################################################
# Reports

class Report:
    """Report of an action. Mainly a namespace with very few methods."""

    def __init__(
            self,
            path,
            target=None,
            success=False,
            log=None,
            depends=None,
        ):
        # pylint: disable=too-many-arguments

        self.depends = depends
        if self.depends is None:
            self.depends = set()

        self.log = log
        if self.log is None:
            self.log = io.StringIO()

        self.path = path
        self.target = target
        self._success = success

    @property
    def full_depends(self):
        """Set of files this action depends on, including ``self.path``."""
        return self.depends | set([self.path.from_fs])

    @property
    def success(self):
        """Success getter"""
        return self._success

    @success.setter
    def success(self, value):
        """Success setter."""
        self._success = value
