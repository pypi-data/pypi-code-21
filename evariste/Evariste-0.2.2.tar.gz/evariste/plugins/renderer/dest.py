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

"""Abstract class for a renderer with a destination folder."""

import os

from evariste import errors, utils
from evariste.plugins.renderer import Renderer

class DestRenderer(Renderer):
    """Abstract class for a renderer with a destination folder."""
    # pylint: disable=too-few-public-methods

    def __init__(self, shared):
        super().__init__(shared)

        if self.local.setup['destdir'] is None:
            self.destdir = self.keyword
        else:
            self.destdir = utils.expand_path(self.local.setup['destdir'])
        try:
            os.makedirs(self.destdir, exist_ok=True)
        except FileExistsError:
            raise errors.EvaristeError("Cannot create directory '{}'.".format(self.destdir))

    def render(self, tree):
        raise NotImplementedError()
