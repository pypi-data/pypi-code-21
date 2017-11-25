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

"""Dummy plugin, used to set default command line arguments.

As evariste relies on some arguments having a value, useful when embedding
evariste into another program.
"""
import os

from evariste import plugins

class Arguments(plugins.PluginBase):
    """Set needed default command line arguments."""
    # pylint: disable=too-few-public-methods

    plugin_type = ""
    keyword = "arguments"
    global_default_setup = {
        'arguments': {
            'jobs':
            os.cpu_count()+1
        }
    }
