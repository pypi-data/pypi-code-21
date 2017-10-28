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


def test_start_command_line(loop):
    got = []

    async def handler(line):
        got.append(line)

    with subprocess.Popen('echo foo; echo bar', shell=True, stdout=PIPE) as p:
        base.start_command_line(
            handler=handler,
            input_file=p.stdout,
            loop=loop)

    assert got == [b'foo\n', b'bar\n']


def test_start_command_line_exiting_early(loop):
    got = []

    async def handler(line):
        got.append(line)
        return True

    with subprocess.Popen('echo foo; echo bar', shell=True, stdout=PIPE) as p:
        base.start_command_line(
            handler=handler,
            input_file=p.stdout,
            loop=loop)

    assert got == [b'foo\n']


def test_start_command_line_pre_hook(loop):
    got = []

    async def handler(line):
        got.append(line)

    def hook():
        got.append(b'pre\n')

    with subprocess.Popen('echo foo; echo bar', shell=True, stdout=PIPE) as p:
        base.start_command_line(
            handler=handler,
            pre_hook=hook,
            input_file=p.stdout,
            loop=loop)

    assert got == [b'pre\n', b'foo\n', b'pre\n', b'bar\n', b'pre\n']
