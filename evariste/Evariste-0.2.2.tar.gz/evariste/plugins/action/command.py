# Copyright Louis Paternault 2017
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

"""Shell command: perform a (list of) shell command(s) on files."""

import logging
import os
import pathlib
import re
import shutil
import shlex
import subprocess
import tempfile
import threading

from evariste import errors
from evariste.hooks import ContextHook
from evariste.plugins.action import Action, PathCompiler, Report
from evariste.utils import yesno
import evariste

LOGGER = logging.getLogger(evariste.__name__)
STRACE_RE = re.compile(r'^\d* *open\("(?P<name>.*)",.*O_RDONLY.*\) = *[^ -].*')

class MissingOption(errors.EvaristeError):
    """No command was provided for action :class:`Command`."""

    def __init__(self, filename, section, option):
        super().__init__()
        self.filename = filename
        self.section = section
        self.option = option

    def __str__(self):
        return (
            "Configuration for file '{file}' is missing option '{option}' in section '{section}'."
            ).format(
                file=self.filename,
                section=self.section,
                option=self.option,
            )

def system_no_strace(command, path, log):
    """Run a system command.

    This function:
    - run command;
    - log standard output and error.
    """

    process = subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        # The following lines, as well as the `.decode(errors='replace')` a few
        # lines below), may be uncommented when support for python3.5 is
        # dropped.
        #universal_newlines=True,
        #errors="replace",
        cwd=path.parent.from_fs.as_posix(),
        )

    log.write(process.communicate()[0].decode(errors="replace"))

    return process.returncode

def system_strace(command, path, log, depends, tempdir):
    """Run a system command, analysing strace output to set `depends` files.

    This function:
    - run command;
    - log standard output and error;
    - track opened files.
    """

    def _process_strace_line(line):
        """Process output line of strace, and complete ``depends`` if relevant."""
        match = STRACE_RE.match(line)
        if match:
            name = pathlib.Path(path.parent.from_fs) / pathlib.Path(match.groupdict()["name"])
            if name.resolve() != path.from_fs.resolve():
                if path.vcs.is_versionned(name):
                    depends.add(name)

    def _process_strace(pipe):
        """Process strace output, to find dependencies."""
        with open(pipe, mode="r", errors="replace") as file:
            for line in file:
                try:
                    _process_strace_line(line)
                except FileNotFoundError:
                    # File was deleted between the time its name is read and
                    # the time we check if it is a dependency: it can be
                    # discarded.
                    pass

    stdout = list(os.pipe())
    stderr = list(os.pipe())
    fifo = os.path.join(tempdir, str(id(path)))
    os.mkfifo(fifo)

    process = subprocess.Popen(
        r"""strace -f -o "{dest}" -e trace=open sh -c {command}""".format(
            dest=fifo,
            command=shlex.quote(command),
            ),
        shell=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        pass_fds=stdout + stderr,
        # The following lines, as well as the `.decode(errors='replace')` a few
        # lines below), may be uncommented when support for python3.5 is
        # dropped.
        #universal_newlines=True,
        #errors="replace",
        cwd=path.parent.from_fs.as_posix(),
        )

    strace_thread = threading.Thread(
        target=_process_strace,
        daemon=True,
        kwargs={
            'pipe' : fifo,
            }
        )
    strace_thread.start()
    log.write(process.communicate()[0].decode(errors="replace"))
    os.unlink(fifo)
    strace_thread.join()
    for descriptor in stdout + stderr:
        os.close(descriptor)

    return process.returncode

class CommandCompiler(PathCompiler):
    """Run commands on the path."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._report = None # Temporary report. It will be completed during compilation.

    def iter_commands(self):
        """Iterator over the list of commands."""
        for option in self.path.config[self.keyword]:
            if option.startswith("command"):
                yield self.path.format(
                    self.path.config[self.keyword][option]
                    )

    @property
    def tempdir(self):
        """Return the path of a temporary, as secure as possible, directory."""
        return self.parent.tempdir

    def run_subcommand(self, command):
        """Run the subcommand ``command``."""
        LOGGER.info("Running command: {}".format(command))

        with self.shared.builder.lock.thread_safe():
            if (
                    yesno(self.path.config[self.keyword].get('strace', 'false'))
                ) or (
                    'strace' not in self.path.config[self.keyword]
                    and
                    yesno(self.parent.local.setup['strace'])
                ):
                returncode = system_strace(
                    command=command,
                    path=self._report.path,
                    log=self._report.log,
                    depends=self._report.depends,
                    tempdir=self.tempdir,
                    )
            else:
                returncode = system_no_strace(
                    command=command,
                    path=self._report.path,
                    log=self._report.log,
                    )
        return returncode == 0

    def get_target(self):
        """Return the path of the target."""
        if not self.path.config[self.keyword]['target'] is not None:
            raise MissingOption(self.path.from_fs, self.keyword, 'target')
        return (
            self.path.parent.from_source.as_posix()
            /
            pathlib.Path(self.path.format(self.path.config[self.keyword]["target"]))
            )

    def compile(self):
        """Perform compilation of `self.path`."""
        self._report = Report(
            self.path,
            success=True,
            target=self.get_target(),
            )
        for command in self.iter_commands():
            parsed_command = self.path.format(command)
            self._report.log.write("$ {}\n".format(parsed_command))
            if not self.run_subcommand(parsed_command):
                self._report.success = False
                break
        for regexp in shlex.split(self.path.config[self.parent.keyword].get('depends', '')):
            for name in self.path.parent.from_fs.glob(regexp):
                if name.resolve() != self.path.from_fs.resolve():
                    if self.path.vcs.is_versionned(name):
                        self._report.depends.add(name)
        return self._report

class TempDir(ContextHook):
    """Manage creation and deletion of a temporary directory."""

    def enter(self, *__args, **__kwargs):
        self.plugin.tempdir = tempfile.mkdtemp(
            prefix="evariste-{}-{}-".format(os.getpid(), self.plugin.keyword),
            )

    def exit(self, value=None):
        shutil.rmtree(self.plugin.tempdir)
        return value

class Command(Action):
    """Chain of commands"""

    keyword = "action.command"
    pathcompiler = CommandCompiler
    hooks = {
        'compiletree': TempDir,
        }
    default_setup = {
        'strace': False,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tempdir = None

    def match(self, value):
        return False
