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

"""Compilation of {,La,Lua,Xe}TeX files"""

import pathlib

from evariste import utils
from evariste.plugins.action.command import Command, CommandCompiler

class LatexCompiler(CommandCompiler):
    """Compile path as a *latex file."""

    DEFAULT_COMMANDS = [
        "latex",
        "?bibtex",
        "?makeindex",
        "?latex",
        ]
    PREDEFINED_COMMANDS = {
        'latex': '{latex} {basename}',
        'pdflatex': 'pdflatex {basename}',
        'lualatex': 'lualatex {basename}',
        'xelatex': 'xelatex {basename}',
        'bibtex': '{bibtex} {basename}',
        'biblatex': 'biblatex {basename}',
        'makeindex': 'makeindex {basename}',
        }
    TARGET = {
        'latex': '{basename}.dvi',
        'pdflatex': '{basename}.pdf',
        'lualatex': '{basename}.pdf',
        'xelatex': '{basename}.pdf',
        }
    CONDITIONAL_COMMANDS = [
        'latex',
        'bibtex',
        'makeindex',
        ]
    BIN = {
        'latex': 'latex',
        'bibtex': 'bibtex',
        'makeindex': 'makeindex',
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.latex_todo = 1
        # Reading binaries
        self.bin = self.BIN.copy()
        for key in self.bin:
            if self.path.config[self.keyword][key] is not None:
                if self.path.config[self.keyword][key] is not None:
                    self.bin[key] = self.path.config[self.keyword][key]

    def get_target(self):
        # Setting target
        if not self.path.config[self.keyword]['target'] is not None:
            basetarget = self.path.format(self.TARGET[self.bin['latex']])
        else:
            basetarget = self.path.format(self.path.config[self.keyword]["target"])
        return self.path.parent.from_source / pathlib.Path(basetarget)

    def _format_command(self, command):
        """Iterate over commands that are to be executed."""
        if command.startswith("?") and command[1:] in self.CONDITIONAL_COMMANDS:
            yield from getattr(self, "_conditionnal_command_{}".format(command[1:]))()
        elif command.startswith("!"):
            yield utils.partial_format(command[1:], **self.bin)
        elif command in self.PREDEFINED_COMMANDS:
            yield utils.partial_format(self.PREDEFINED_COMMANDS[command], **self.bin)
        else:
            yield utils.partial_format(command, **self.bin)

    def iter_commands(self):

        precommands = []
        postcommands = []
        commands = []
        if self.keyword in self.path.config:
            for option in self.path.config[self.keyword]:
                if option.startswith("pre"):
                    precommands.append("!{}".format(self.path.config[self.keyword][option]))
                elif option.startswith("cmd"):
                    commands.append(self.path.config[self.keyword][option])
                elif option.startswith("post"):
                    postcommands.append("!{}".format(self.path.config[self.keyword][option]))
        if not commands:
            commands = self.DEFAULT_COMMANDS

        for command in precommands + commands + postcommands:
            yield from self._format_command(command)

    def _conditionnal_command_bibtex(self):
        """Yield a bibtex command, if necessary.

        "Necessary" means that option 'bibtex' appears in configuration file.

        It might be detected, some day, by looking at the LaTeX log.
        """
        if self.path.config[self.keyword]['bibtex'] is not None:
            self.latex_todo += 1
            yield from self._format_command('bibtex')

    def _conditionnal_command_makeindex(self):
        """Yield a makeindex command, if necessary.

        "Necessary" means that option 'makeindex' appears in configuration file.

        It might be detected, some day, by looking at the LaTeX log.
        """
        if self.path.config[self.keyword]['makeindex'] is not None:
            self.latex_todo += 1
            yield from self._format_command('makeindex')

    def _conditionnal_command_latex(self):
        """Yield as many `latex` commands as necessary.

        Previous commands may have incremented `self.latex_todo`.
        """
        while self.latex_todo != 0:
            self.latex_todo -= 1
            yield from self._format_command('latex')

class Latex(Command):
    """Compilation of *TeX files."""

    keyword = "action.latex"
    priority = 100
    pathcompiler = LatexCompiler

    def match(self, value):
        return value.suffix == ".tex"
