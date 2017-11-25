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

"""Access to VCS (git, etc.) versionned files."""

from datetime import datetime
import os
import pathlib

from evariste import errors, plugins
from evariste.tree import Root

class NoRepositoryError(errors.EvaristeError):
    """No repository contains the given path."""

    def __init__(self, vcstype, directory):
        super().__init__()
        self.directory = directory
        self.vcstype = vcstype

    def __str__(self):
        return (
            "Could not find any {} repository containing directory '{}'."
            ).format(
                self.vcstype,
                self.directory,
                )

class VCS(plugins.PluginBase):
    """Generic class to access to versionned files."""

    plugin_type = "vcs"
    global_default_setup = {'setup': {'source': '.'}}

    @property
    def source(self):
        """Return an absolute version of source setup option."""
        return pathlib.Path(self.shared.setup['setup']['source'])

    def walk(self):
        """Iterate over list of versionned files, descendants of source (as defined by setup file).
        """
        raise NotImplementedError()

    def is_versionned(self, path):
        """Return ``True`` iff ``path`` is versionned."""
        raise NotImplementedError()

    @property
    def workdir(self):
        """Return path of the root of the repository."""
        raise NotImplementedError()

    def from_repo(self, path):
        """Return ``path``, relative to the repository root."""
        return os.path.relpath(
            path.resolve().as_posix(),
            self.workdir
            )


    def last_modified(self, path):
        """Return the datetime of last modification."""
        # pylint: disable=no-self-use
        return datetime.fromtimestamp(os.path.getmtime(str(path)))
