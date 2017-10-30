# Copyright (C) 2017 Allen Li
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess
from subprocess import PIPE

from mir.acle import base
from mir.acle import handlers


def test_BaseHandler_exception(loop, capsys):
    class Handler(handlers.BaseHandler):

        async def _call(self, line: str):
            raise _TestError

    handler = Handler()

    with subprocess.Popen('echo foo; echo bar', shell=True, stdout=PIPE) as p:
        base.start_command_line(
            handler=handler,
            input_file=p.stdout,
            loop=loop)

    out, err = capsys.readouterr()
    assert out == 'Uncaught exception in command line handler\n' * 2


def test_ShellHandler(loop):
    got = []

    async def handle(args):
        got.append(args)

    handler = handlers.ShellHandler()
    handler.add_command('foo', handle)

    with subprocess.Popen('echo foo -d thing', shell=True, stdout=PIPE) as p:
        base.start_command_line(
            handler=handler,
            input_file=p.stdout,
            loop=loop)

    assert got == [['foo', '-d', 'thing']]


def test_ShellHandler_default_empty_command(loop):
    handler = handlers.ShellHandler()
    with subprocess.Popen('echo', shell=True, stdout=PIPE) as p:
        # Should not raise
        base.start_command_line(
            handler=handler,
            input_file=p.stdout,
            loop=loop)


def test_ShellHandler_default_unknown_command(loop, capsys):
    handler = handlers.ShellHandler()

    with subprocess.Popen('echo foo -d thing', shell=True, stdout=PIPE) as p:
        base.start_command_line(
            handler=handler,
            input_file=p.stdout,
            loop=loop)

    out, err = capsys.readouterr()
    assert out == 'Unknown command foo\n'


def test_ShellHandler_custom_default_handler(loop):
    got = []

    async def handle(args):
        got.append(args)

    handler = handlers.ShellHandler()
    handler.set_default_handler(handle)

    with subprocess.Popen('echo foo -d thing', shell=True, stdout=PIPE) as p:
        base.start_command_line(
            handler=handler,
            input_file=p.stdout,
            loop=loop)

    assert got == [['foo', '-d', 'thing']]


class _TestError(Exception):
    pass
