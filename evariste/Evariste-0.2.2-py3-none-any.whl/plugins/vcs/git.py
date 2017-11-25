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

"""Access to git-versionned files."""

from datetime import datetime
import logging
import os

import git

from evariste.plugins.vcs import VCS, NoRepositoryError

LOGGER = logging.getLogger(__name__)

class Git(VCS):
    """Access git-versionned files"""
    # pylint: disable=no-member

    keyword = "vcs.git"

    def __init__(self, shared):
        super().__init__(shared)
        try:
            self.repository = git.Repo(str(self.source), search_parent_directories=True)
        except git.InvalidGitRepositoryError:
            raise NoRepositoryError(self.keyword, self.source)

        self._last_modified = self._read_modification_date()

    def _read_modification_date(self):
        """Return a dictionary of versionned files and their last modification time."""
        LOGGER.info("Reading git commit dates…")
        last_modified = {}
        no_known_date = set((blob.path for blob in self.repository.tree().traverse()))
        for commit in self.repository.iter_commits():
            new = no_known_date & commit.stats.files.keys()
            for path in new:
                last_modified[path] = datetime.fromtimestamp(commit.committed_date)
                no_known_date.remove(path)
            if not no_known_date:
                break
        for blob in self.repository.index.iter_blobs():
            if blob[1].path not in last_modified:
                last_modified[blob[1].path] = super().last_modified(
                    os.path.join(self.workdir, blob[1].path)
                    )
        LOGGER.info("Done")
        return last_modified


    def walk(self):
        source = self.source.resolve().as_posix()
        for entry in self._last_modified:
            path = os.path.join(self.workdir, entry)
            if path.startswith(source):
                yield os.path.relpath(path, source)

    def is_versionned(self, path):
        return self.from_repo(path) in self._last_modified

    @property
    def workdir(self):
        return self.repository.working_dir

    def last_modified(self, path):
        if not self.is_versionned(path):
            return super().last_modified(path)

        return self._last_modified[self.from_repo(path)]
