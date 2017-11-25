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

"""Plugin to copy files at the end of compilation and rendering."""

import glob

from evariste import plugins, utils
from evariste.hooks import ContextHook

class _Close(ContextHook):
    """Hook to copy files at the end of compilation."""

    def exit(self, value=None):
        for key in self.local.setup:
            if key.startswith("copy"):
                if isinstance(self.local.setup[key], str):
                    arguments = self.local.setup[key].split()
                else:
                    arguments = self.local.setup[key]
                try:
                    sources, dest = arguments
                except (ValueError, TypeError):
                    raise ValueError(
                        """[copy] Option "{}" should be "SOURCE DEST".""".format(key)
                        )
                if dest is None:
                    continue
                for path in glob.iglob(sources):
                    utils.copytree(path, dest)
        return value

class Copy(plugins.PluginBase):
    """Copy files at the end of compilation."""
    # pylint: disable=too-few-public-methods

    plugin_type = ""
    keyword = "copy"
    hooks = {
        'close': _Close,
        }
