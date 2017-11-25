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

"""Raw action: does nothing; simply provides a link to download file."""

from evariste.plugins.action import Action, PathCompiler, Report

class RawCompiler(PathCompiler):
    """Raw compiler: does nothing to the file."""
    # pylint: disable=too-few-public-methods

    def compile(self):
        return Report(
            self.path,
            target=self.path.from_source,
            success=True,
            )


class Raw(Action):
    """Raw action"""

    keyword = "action.raw"
    priority = -float("inf")
    pathcompiler = RawCompiler

    def match(self, value):
        return True
