# -*- coding: utf-8 -*-
"""
Clik extension for adding an interactive command shell to an application.

:author: Joe Joyce <joe@decafjoe.com>
:copyright: Copyright (c) Joe Joyce and contributors, 2017.
:license: BSD
"""
from __future__ import print_function

import cmd
import contextlib
import shlex

from clik.argparse import ArgumentParser, ArgumentParserExit


__all__ = ['BaseShell', 'DefaultShell', 'exclude_from_shell']

#: Unique object used to indicate that a command should not be present
#: in the shell.
#:
#: :type: ``object``
EXCLUDE = object()


def exclude_from_shell(command_or_fn):
    """
    Exclude command from the shell interface.

    This decorator can be applied before or after the command decorator::

      @exclude_from_shell
      @myapp
      def mycommand():

      # is the same as

      @myapp
      @exclude_from_shell
      def mycommand():

    :param command_or_fn: Command instance or function
    :type command_or_fn: :class:`clik.command.Command` or function
    :return: Whatever was passed in
    """
    command_or_fn._clik_shell = EXCLUDE
    return command_or_fn


def get_shell_subcommands_for(parent_command):
    """
    Return list of command objects that should be present in the shell.

    This excludes the commands that have been marked with
    :func:`exclude_from_shell`.

    :param command: Command for which to get shell subcommands
    :type command: :class:`clik.command.Command`
    :return: List of commands that should be present in the shell
    :rtype: :class:`list` of :class:`clik.command.Command` instances
    """
    rv = []
    for child in parent_command._children:
        if getattr(child, '_clik_shell', None) is not EXCLUDE \
           and getattr(child._fn, '_clik_shell', None) is not EXCLUDE:
            rv.append(child)
    return rv


@contextlib.contextmanager
def parser_for(command):
    """
    Context manager that creates a root parser object for ``command``.

    See :func:`make_action_method` and :func:`make_help_method` for usage.

    :param command: Command for which to create a parser
    :type command: :class:`clik.command.Command`
    :return: Argument parser for the command
    :rtype: :class:`argparse.ArgumentParser`
    """
    description, epilog = command._split_docstring(command._fn)
    parser = ArgumentParser(
        prog=command._name,
        description=description,
        epilog=epilog,
    )
    with command._ctx(args=None):
        command._configure_parser(parser)
    try:
        yield parser
    except ArgumentParserExit:
        print()


def make_action_method(command):
    """
    Dynamically generate the ``do_`` method for ``command``.

    :param command: Command for which to generate ``do_`` method
    :type command: :class:`clik.command.Command`
    :return: Method that calls the given command
    :rtype: ``fn(self, line)``
    """
    def method(self, line):
        with parser_for(command) as parser:
            with command._ctx(args=parser.parse_args(shlex.split(line))):
                ec = command._run()
                if ec:
                    self.error(ec)
    return method


def make_help_method(command):
    """
    Dynamically generate the ``help_`` method for ``command``.

    :param command: Command for which to generate ``help_`` method
    :type command: :class:`clik.command.Command`
    :return: Method that prints the help for the given command
    :rtype: ``fn(self)``
    """
    def method(self):
        with parser_for(command) as parser:
            parser.parse_args(('-h',))
    return method


class BaseShell(cmd.Cmd):
    """Minimal implementation to integrate clik and cmd."""

    #: Prompt for the command loop. If ``None``, the prompt is set to
    #: ``"name> "``, where ``name`` is the name of the root command
    #: object.
    #:
    #: :type: :class:`str` or ``None``
    prompt = None

    def __init__(self, command):
        """
        Instantiate the command loop.

        :param command: "Root" command object (usually the application object
                        created by :func:`clik.app.app`)
        :type command: :class:`clik.command.Command`
        """
        if self.prompt is None:
            self.prompt = '%s> ' % command._name
        cls = self.__class__
        cls._action_methods = {}
        for subcommand in get_shell_subcommands_for(command):
            method_name = subcommand._name.replace('-', '_')

            action_method = make_action_method(subcommand)
            cls._action_methods[subcommand._name] = action_method
            setattr(cls, 'do_%s' % method_name, action_method)
            for alias in subcommand._aliases:
                cls._action_methods[alias] = action_method
                setattr(cls, 'do_%s' % alias.replace('-', '_'), action_method)

            help_method = make_help_method(subcommand)
            setattr(cls, 'help_%s' % method_name, help_method)
        super(BaseShell, self).__init__()

    def default(self, line):
        """
        Override that hackily supports commands with hyphens.

        See the quickstart in the documentation for further explanation.

        :param str line: Line whose command is unrecognized
        :rtype: ``None``
        """
        name = line.split()[0]
        if name in self._action_methods:
            return self._action_methods[name](self, line)
        print('error: unregonized command:', name, '(enter ? for help)\n')

    def error(self, exit_code):
        """
        Handle non-zero subcommand exit code.

        By default, this prints a generic error message letting the user know
        the exit code.

        :param int exit_code: Exit code from the subcommand
        :rtype: ``None``
        """
        print('error: command exited with status %s\n' % exit_code)


class DefaultShell(BaseShell):
    """Command loop subclass that implements commonly desire facilities."""

    def cmdloop(self):
        """Override that supports graceful handling of keyboard interrupts."""
        try:
            super(DefaultShell, self).cmdloop()
        except KeyboardInterrupt:
            print()

    def do_EOF(self, _):  # noqa: N802 (EOF must be capitalized)
        """Exit the shell."""
        print('\n')
        return True

    def do_exit(self, _):
        """Exit the shell."""
        print()
        return True

    def do_quit(self, _):
        """Exit the shell."""
        print()
        return True

    def emptyline(self):
        """
        Override that turns an empty line into a no-op.

        By default, the command loop runs the previous command when an empty
        line is received. This is bad default behavior because it's not what
        users expect.

        If "run the last command" is the desired behavior, you should extend
        :class:`BaseClass` rather than this class.
        """
