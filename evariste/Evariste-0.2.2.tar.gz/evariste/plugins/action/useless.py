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

"""Useless action. Nothing has changed since last compilation."""

import pathlib
import io

from evariste.plugins.action import Action, PathCompiler, Report

class UselessCompiler(PathCompiler):
    """Does nothing to compile path (most likely because it is cached)."""
    # pylint: disable=too-few-public-methods

    def compile(self):
        cached = self.shared.tree[self.path.from_source]['changed']
        if cached is None:
            target = self.path.from_source
            depends = set()
        else:
            fs_target = pathlib.Path(list(cached['target'].keys())[0])
            target = fs_target.relative_to(self.path.root.from_fs)
            depends = set([
                pathlib.Path(path)
                for path
                in cached['depends'].keys()
                ]) - set([self.path.from_fs])
        return Report(
            self.path,
            target=target,
            depends=depends,
            success=True,
            log=io.StringIO(self.shared.tree[self.path.from_source]['cachelog']),
            )

class Useless(Action):
    """Useless action. Nothing has changed since last compilation."""

    keyword = "action.useless"
    pathcompiler = UselessCompiler
    required = True
