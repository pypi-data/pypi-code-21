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

"""Command line handlers

This module implements command line handlers for mir.acle.base.
"""

import logging
import shlex

logger = logging.getLogger(__name__)


class BaseHandler:

    """Base command line handler implementation

    This handles some no-brainer things like converting the command line
    from bytes to str and catching all exceptions so the command line
    does not crash.

    Subclasses should implement _call().
    """

    async def __call__(self, line: bytes):
        try:
            return await self._call(line.decode())
        except Exception:
            logger.exception('Uncaught exception in command line handler')
            print('Uncaught exception in command line handler')

    async def _call(self, line: str):  # pragma: no cover
        pass


class ShellHandler(BaseHandler):

    """Implements shell-like command handling

    Each command line is split into words like a POSIX shell, and the
    first word is interpreted as the command.  The handler for the
    command is looked up and called with all arguments, which includes
    command itself.
    """

    def __init__(self, tokenizer=None):
        if tokenizer is None:  # pragma: no cover
            tokenizer = shlex.split
        self._tokenizer = tokenizer
        self._commands = dict()

    def set_default_handler(self, handler):
        """Set the default handler for unknown or empty commands.

        handler should take one argument, a list of strings.
        """
        self._default_handler = handler

    def add_command(self, command, handler):
        """Add a handler for a command.

        handler should take one argument, a list of strings.
        """
        self._commands[command] = handler

    async def _call(self, line: str):
        args = self._tokenizer(line)
        handler = self._get_handler(args)
        return await handler(args)

    def _get_handler(self, args):
        if not args:
            return self._default_handler
        command = args[0]
        return self._commands.get(command, self._default_handler)

    async def _default_handler(self, args):
        """Default handler for empty or unknown commands.

        Prints an error message for unknown commands and does nothing
        for empty commands.

        This can be overridden on an instance by calling
        set_default_handler().
        """
        if args:
            print(f'Unknown command {args[0]}')
