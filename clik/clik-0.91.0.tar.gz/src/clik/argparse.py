# -*- coding: utf-8 -*-
"""
Most of the hackery that makes clik tick.

:author: Joe Joyce <joe@decafjoe.com>
:copyright: Copyright (c) Joe Joyce and contributors, 2009-2017.
:license: BSD
"""
from __future__ import absolute_import, print_function
import argparse
import contextlib
import sys

from clik.compat import PY2, PY26, PY33


#: Name of the argument that contains whether to allow unknown
#: arguments.
#:
#: :type: :class:`str`
ALLOW_UNKNOWN = '_clik_unknown'


class ArgumentParserExit(Exception):
    """Raised instead of allowing :mod:`argparse` to call :func:`sys.exit`."""

    def __init__(self, code):
        """
        Initialize the exception.

        :param int code: Exit code.
        """
        fmt = 'argument parser exited with return code %i'
        super(ArgumentParserExit, self).__init__(fmt % code)

        #: Exit code.
        #:
        #: :type: :class:`int`
        self.code = code


class BareUnsupportedFeatureError(Exception):
    """Raised when using a feature that is not supported by bare commands."""

    def __init__(self, feature):
        """
        Initialize the exception.

        :param str feature: Name of the feature that is unsupported.
        """
        msg = 'Feature is not supported for bare commands: %s' % feature
        super(BareUnsupportedFeatureError, self).__init__(msg)

        #: Feature that is unsupported.
        #:
        #: :type: :class:`str`
        self.feature = feature


class UnknownArgsUnsupportedError(Exception):
    """Raised when trying to allow unknown args on a command with children."""

    def __init__(self):
        """Initialize the exception."""
        msg = 'Unknown args are not allowed for commands with subcommands'
        super(UnknownArgsUnsupportedError, self).__init__(msg)


class HelpFormatter(argparse.HelpFormatter):
    """Format usage with no trailing newline on usage."""

    def _format_usage(self, *args, **kwargs):
        parent = super(HelpFormatter, self)
        return parent._format_usage(*args, **kwargs)[:-1]


class ArgumentParser(argparse.ArgumentParser):
    """:class:`argparse.ArgumentParser` specialized for clik."""

    def __init__(self, *args, **kwargs):
        """Initialize -- same arguments as :class:`argparse.ArgumentParser`."""
        self._clik_bare_command_mode = False
        self._clik_bare_dests = None
        self._clik_command = None
        kwargs.setdefault('formatter_class', HelpFormatter)
        super(ArgumentParser, self).__init__(*args, **kwargs)

    def exit(self, status=0, message=None):
        """
        Override default behavior to avoid interpreter exit.

        By default, the parser calls :func:`sys.exit`. In certain situations --
        namely testing -- we don't actually want to exit the Python
        interpreter.

        So instead of exiting, this throws an :exc:`ArgumentParserExit`
        exception which can be caught by the caller.

        :param int status: Exit status.
        :param str message: Optional message. If supplied, will be printed
                            to :data:`sys.stderr` before raising the exception.
        :raise: :exc:`ArgumentParserExit`
        """
        if message:
            print(message, end='', file=sys.stderr)
        raise ArgumentParserExit(status)

    @contextlib.contextmanager
    def _clik_bare_arguments(self):
        """
        Context manager for bare command mode.

        When the parser is in bare command mode, it disallows certain features
        (like positional args and mutually exclusive groups). In addition, the
        argument destinations are recorded in order to do some post-processing
        before running the selected command.
        """
        self._clik_bare_dests = []
        self._clik_bare_command_mode = True
        yield
        self._clik_bare_command_mode = False

    def add_argument(self, *args, **kwargs):
        """
        Override default behavior to disallow posargs in bare commands.

        :raise: :class:`BareUnsupportedFeatureError` if adding a positional
                argument to a bare command.
        """
        argument = super(ArgumentParser, self).add_argument(*args, **kwargs)
        if self._clik_bare_command_mode:
            if argument.nargs:
                msg = 'positional arguments (dest: %s)' % argument.dest
                raise BareUnsupportedFeatureError(msg)
            self._clik_bare_dests.append(argument.dest)
        return argument

    def add_mutually_exclusive_group(self, *args, **kwargs):
        """
        Override default behavior to disallow mutex groups in bare commands.

        :raise: :class:`BareUnsupportedFeatureError` if adding a mutually
                exclusive group to a bare command.
        """
        if self._clik_bare_command_mode:
            raise BareUnsupportedFeatureError('mutually exclusive groups')
        s = super(ArgumentParser, self)
        return s.add_mutually_exclusive_group(*args, **kwargs)

    def allow_unknown_args(self):
        """
        Allow unknown arguments, putting them in ``clik.unknown_args``.

        :raise: :exc:`UnknownArgsUnsupportedError` if this parser has
                subparsers -- unknown arguments are allowed *only* on
                leaf commands.
        """
        if self._clik_command._children:
            raise UnknownArgsUnsupportedError
        self.set_defaults(**{ALLOW_UNKNOWN: True})

    def _clik_format_usage(self, formatter):
        bare_dests = self._clik_bare_dests
        actions, bare_actions, subparsers = [], [], None
        for action in self._actions:
            if isinstance(action, argparse._SubParsersAction):
                subparsers = action
                actions.append(action)
            else:
                bare_actions.append(action)
                if bare_dests is None or action.dest not in bare_dests:
                    actions.append(action)
        prefix = 'usage: '
        mutex_groups = self._mutually_exclusive_groups
        if bare_dests is None or subparsers:
            formatter.add_usage(self.usage, actions, mutex_groups, prefix)
            prefix = '       '
        if bare_dests is not None:
            formatter.add_usage(self.usage, bare_actions, mutex_groups, prefix)
        return formatter

    def format_usage(self):
        """Override default behavior to use clik's formatter."""
        return self._clik_format_usage(self._get_formatter()).format_help()

    def format_help(self):
        """Override default behavior to support formatting bare commands."""
        formatter = self._get_formatter()
        self._clik_format_usage(formatter)
        formatter.add_text('\n')
        formatter.add_text(self.description)
        for action_group in self._action_groups:
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()
        formatter.add_text(self.epilog)
        return formatter.format_help()


if PY33 or PY26:  # pragma: no cover (~copypaste of Python 3.4 implementation)
    # LINT: Ignore undocumented function violation. Compatibility code is not
    #       formally documented.
    def __call__(self, parser, namespace, values, option_string=None):  # noqa
        parser_name = values[0]
        arg_strings = values[1:]

        if self.dest is not argparse.SUPPRESS:
            setattr(namespace, self.dest, parser_name)

        try:
            parser = self._name_parser_map[parser_name]
        except KeyError:
            fmt = 'unknown parser %(parser_name)r (choices: %(choices)s)'
            args = {
                'parser_name': parser_name,
                'choices': ', '.join(self._name_parser_map),
            }
            raise argparse.ArgumentError(self, fmt % args)

        subnamespace, arg_strings = parser.parse_known_args(arg_strings, None)
        for key, value in vars(subnamespace).items():
            setattr(namespace, key, value)

        if arg_strings:
            vars(namespace).setdefault(argparse._UNRECOGNIZED_ARGS_ATTR, [])
            attr = getattr(namespace, argparse._UNRECOGNIZED_ARGS_ATTR)
            attr.extend(arg_strings)

    argparse._SubParsersAction.__call__ = __call__


if PY2:
    original_error = ArgumentParser.error

    # LINT: Ignore undocumented function violation. Compatibility code is not
    #       formally documented.
    def error(self, message=None):  # noqa: D103
        if message == 'too few arguments':
            for action in self._actions:  # pragma: no branch (unreachable)
                if isinstance(action, argparse._SubParsersAction):
                    break
            else:  # pragma: no cover (unreachable)
                raise Exception('this code should be unreachable')
            if action.required:
                self.print_usage(sys.stderr)
                fmt = '%s: error: the following arguments are required: %s\n'
                return self.exit(2, fmt % (self.prog, action.metavar))
        else:
            return original_error(self, message)

    ArgumentParser.error = error

    # https://gist.github.com/sampsyo/471779

    # LINT: Ignore undocumented function violation. Compatibility code is not
    #       formally documented.
    class _AliasedSubParsersPseudoAction(argparse.Action):  # noqa: D103
        def __init__(self, name, aliases, help):
            dest = name
            if aliases:
                dest += ' (%s)' % ', '.join(aliases)
            parent = super(_AliasedSubParsersPseudoAction, self)
            parent.__init__(option_strings=[], dest=dest, help=help)

    original_add_parser = argparse._SubParsersAction.add_parser

    # LINT: Ignore undocumented function violation. Compatibility code is not
    #       formally documented.
    def add_parser(self, name, **kwargs):  # noqa: D103
        aliases = kwargs.pop('aliases')
        parser = original_add_parser(self, name, **kwargs)
        for alias in aliases:
            self._name_parser_map[alias] = parser
        help = kwargs.pop('help')
        self._choices_actions.pop()
        action = _AliasedSubParsersPseudoAction(name, aliases, help)
        self._choices_actions.append(action)
        return parser

    argparse._SubParsersAction.add_parser = add_parser
