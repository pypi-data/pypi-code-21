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

"""acle base implementation

This module implements the very basic functionality for an async command
line loop.
"""

import asyncio
import sys


def start_command_line(handler, *, pre_hook=lambda: None,
                       input_file=None, loop=None):
    """Start an asynchronous command line.

    handler is a coroutine function which is called with each command
    line as a string or bytestring read from input_file.  If handler
    returns True or input_file reaches EOF, the command line exits.

    pre_hook is a function that is called before each command line is
    read.

    input_file is a file object to read commands from.  If missing, use
    stdin.  input_file should be backed by a socket or pipe.

    loop is the asyncio event loop to use.  If missing, use
    asyncio.get_event_loop().
    """
    if input_file is None:  # pragma: no cover
        input_file = sys.stdin
    if loop is None:  # pragma: no cover
        loop = asyncio.get_event_loop()
    loop.run_until_complete(_mainloop(loop, handler, pre_hook, input_file))


async def _mainloop(loop, handler, pre_hook, input_file):
    reader = await async_reader(loop, input_file)
    while True:
        pre_hook()
        line = await reader.readline()
        if not line:
            break
        if await handler(line):
            break


async def async_reader(loop, file):
    """Create an asyncio StreamReader."""
    reader = asyncio.StreamReader()
    reader_protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: reader_protocol, file)
    return reader
