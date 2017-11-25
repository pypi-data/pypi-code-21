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

"""Dummy, do-nothing vcs. Used for tests."""

from datetime import datetime
import os

from evariste.plugins.vcs import VCS

class NoneVCS(VCS):
    """Dummy vcs"""

    keyword = "vcs.none"

    def walk(self):
        yield from []

    def is_versionned(self, path):
        return False

    @property
    def workdir(self):
        return os.getcwd()

    def from_repo(self, path):
        return os.path.relpath(
            path.resolve().as_posix(),
            self.workdir
            )

    def last_modified(self, path):
        return datetime.fromtimestamp(os.path.getmtime(str(path)))
