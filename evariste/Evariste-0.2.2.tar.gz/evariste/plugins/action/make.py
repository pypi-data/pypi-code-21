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

"""Compilation using `make` binary"""

import pathlib

from evariste.plugins.action.command import Command, CommandCompiler

class MakeCmdCompiler(CommandCompiler):
    """Compilation using `make` binary"""

    def iter_commands(self):
        yield "{bin} {options} {target}".format(
            bin=self.parent.local.setup['bin'],
            options=self.parent.local.setup['options'],
            target=pathlib.Path(self.path.format(self.path.config[self.keyword]["target"])),
            )

class MakeCmd(Command):
    """Compilation using `make` binary"""

    keyword = "action.make"
    priority = 50
    pathcompiler = MakeCmdCompiler
    default_setup = {
        'bin': 'make',
        'options': '',
        }
