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

"""Compilation using commands depending on mimetype or file extensions"""

import mimetypes
import operator
import pathlib
import shlex
import re

from evariste.plugins.action.command import Command, CommandCompiler

class AutoCmdCompiler(CommandCompiler):
    """Compilation using rules based on extension and mimetypes"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup = self.parent.get_command(self.path.from_fs)['setup']

    def get_target(self):
        return (
            self.path.parent.from_source.as_posix()
            /
            pathlib.Path(self.path.format(self._setup['target']))
            )

    def iter_commands(self):
        yield from sorted([self._setup[key] for key in self._setup if key.startswith('command')])

class AutoCmd(Command):
    """Compilation using rules based on mimetypes and extensions"""

    keyword = "action.autocmd"
    priority = 50
    pathcompiler = AutoCmdCompiler

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Parsing setup to build the command dictionary
        self._commands = {}
        for (key, setup) in self.shared.setup.items():
            if key.startswith(self.keyword):
                local = {
                    'setup': setup
                    }

                if setup['priority'] is None:
                    local['priority'] = (1, key)
                else:
                    local['priority'] = (0, int(setup['priority']))
                local['mimetypes'] = setup['mimetypes']
                if local['mimetypes'] is None:
                    local['mimetypes'] = ""
                local['extensions'] = setup['extensions']
                if local['extensions'] is None:
                    local['extensions'] = ""

                local['mimetypes'] = [
                    re.compile(regexp)
                    for regexp
                    in shlex.split(local['mimetypes'])
                    ]
                local['extensions'] = [
                    "." + ext
                    for ext
                    in shlex.split(local['extensions'])
                    ]
                if (not local['mimetypes']) and (not local['extensions']):
                    local['extensions'] = [key[len(self.keyword):]]
                self._commands[key] = local

    def get_command(self, value):
        """Return the command associated with the given file.

        May return ``None`` if no command is associated with it.
        """
        for setup in sorted(self._commands.values(), key=operator.itemgetter('priority')):
            if value.suffix in setup['extensions']:
                return setup
            for regexp in setup['mimetypes']:
                mime = mimetypes.guess_type(str(value))[0]
                if isinstance(mime, str):
                    if regexp.match(mime):
                        return setup
        return None

    def match(self, value):
        return self.get_command(value) is not None
