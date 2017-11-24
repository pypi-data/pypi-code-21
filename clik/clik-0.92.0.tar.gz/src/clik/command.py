# -*- coding: utf-8 -*-
"""
All the recursive, argument-parsin', context-managin' goodness.

:author: Joe Joyce <joe@decafjoe.com>
:copyright: Copyright (c) Joe Joyce and contributors, 2009-2017.
:license: BSD
"""
from __future__ import print_function
import re
import sys


#: Globally-unique value used by commands to indicate they want clik to send
#: the exception (if one occurred) in addition to the child exit code in
#: response to a ``yield``.
#:
#: :type: :class:`object`
catch = object()

#: Name of the magic variable containing the parsed arguments.
#:
#: :type: :class:`str`
ARGS = 'args'

#: Name of the argument that contains the stack of commands to be run.
#:
#: :type: :class:`str`
STACK = '_clik_stack'

#: If a parent has more than this number of subcommands, the help output will
#: ``{command}`` instead of the full list of subcommands.
#:
#: :type: :class:`int`
SHOW_SUBCOMMANDS = 3


class BareAlreadyRegisteredError(Exception):
    """Raised when a bare command has already been registered."""

    def __init__(self, command):
        """
        Initialize the exception.

        :param command: Command the user is trying to register.
        :type command: :class:`Command`
        """
        fmt = 'Bare command already registered for command "%s"'
        super(BareAlreadyRegisteredError, self).__init__(fmt % command._name)

        #: Command caller was trying to register as the bare command.
        #:
        #: :type: :class:`Command`
        self.command = command


class Command(object):
    """The invisible backend driving most of what the user interacts with."""

    @staticmethod
    def _split_docstring(x=None):
        parts = list(filter(None, re.split(r'\n\s*\n', x.__doc__ or '', 1)))
        return parts + [None] * (2 - len(parts))

    def __init__(self, ctx, fn, name=None, alias=None, aliases=None):
        """
        Initialize the command object.

        :param ctx: Context object.
        :type ctx: :class:`clik.context.Context`
        :param fn: Generator function -- the actual command.
        :param str name: Name of the command or ``None``. If ``None``, name
                         will be ``fn.__name__``.
        :param str alias: Command alias or ``None``. If ``None``, the command
                          has no aliases. If this and ``aliases`` are both
                          supplied, ``alias`` will be prepended to the
                          ``aliases`` list.
        :param aliases: List of additional aliases for the command or ``None``.
        :type aliases: :class:`list` or ``None``
        """
        #: Tuple of aliases for this command.
        #:
        #: :type: :class:`tuple` of :class:`str`
        self._aliases = ()

        #: :class:`Command` instance for the bare command or ``None`` if bare
        #: command is not set.
        #:
        #: :type: :class:`Command` or ``None``
        self._bare = None

        #: List of child commands.
        #:
        #: :type: :class:`list` of :class:`Command` instances
        self._children = []

        #: Context object for this command. This context is shared between all
        #: command instances associated with a :class:`clik.app.App`.
        #:
        #: :type: :class:`clik.context.Context`
        self._ctx = ctx

        #: Generator function -- the actual command.
        #:
        #: :type: generator function
        self._fn = fn

        #: In-progress generator for :attr:`_fn`. This is the object that we
        #: call :meth:`generator.send` and :meth:`generator.next` on.
        #:
        #: :type: :class:`generator`
        self._generator = None

        #: Canonical name of the command.
        #:
        #: :type: :class:`str`
        self._name = 'Unnamed'

        #: Parent command. For the root :class:`clik.app.App` instance, this
        #: is ``None``. Set in :meth:`_configure_parser`.
        #:
        #: :type: :class:`Command` or ``None``
        self._parent = None

        #: Parser for this command. Set in :meth:`_configure_parser`.
        #:
        #: :type: :class:`clik.argparse.ArgumentParser`
        self._parser = None

        if name is None:
            self._name = fn.__name__
        else:
            self._name = name

        if aliases is None:
            aliases = []
        else:
            aliases = list(aliases)
        if alias is not None:
            aliases.insert(0, alias)
        self._aliases = tuple(aliases)

    def bare(self, fn):
        """
        Register a bare command.

        :param fn: Generator function -- the bare command.
        :raise: :exc:`BareAlreadyRegisteredError` if a bare command has already
                been registered.
        """
        if self._bare is not None:
            raise BareAlreadyRegisteredError(self)
        self._bare = Command(self._ctx, fn)
        return self._bare

    def __call__(self, fn=None, name=None, alias=None, aliases=None):
        """
        Add subcommands to this command.

        Basic use::

            @myapp
            def mysubcommand():
                yield

        Customizing the subcommand::

            @myapp(name='subcommand', alias='sub', aliases=['s'])
            def mysubcommand():
                yield

        :param fn: Generator function or ``None``. If ``fn`` is supplied,
                   all other arguments are ignored.
        :param str name: Name of the command or ``None``.
        :param str alias: Command alias. See :meth:`__init__` for information
                          on how aliases are handled.
        :param aliases: List of additional aliases for the command or ``None``.
        :type aliases: :class:`list` or ``None``
        """
        def decorate(fn):
            self._children.append(Command(self._ctx, fn, name, alias, aliases))
            return self._children[-1]
        if fn is None:
            return decorate
        return decorate(fn)

    def _configure_parser(self, parser, parent=None, stack=None):
        self._parser = parser
        parser._clik_command = self

        if stack is None:
            stack = []
        if parent is not None:
            self._parent = parent

        self._generator = self._fn()
        with self._ctx(parser=parser):
            ec = next(self._generator)
            if ec:
                return ec

        stack = stack + [self]
        if self._bare:
            self._bare._generator = self._bare._fn()
            with parser._clik_bare_arguments():
                with self._ctx(parser=parser):
                    ec = next(self._bare._generator)
                    if ec:
                        return ec
            parser.set_defaults(**{STACK: stack + [self._bare]})

        if self._children:
            if len(self._children) > SHOW_SUBCOMMANDS:
                metavar = '{command}'
            else:
                names = ','.join([c._name for c in self._children])
                metavar = '{%s}' % names
            subparsers = parser.add_subparsers(
                dest='command',
                metavar=metavar,
                title='subcommands',
            )
            if not self._bare:
                subparsers.required = True
            for child in self._children:
                description, epilog = self._split_docstring(child._fn)
                subparser = subparsers.add_parser(
                    child._name,
                    aliases=child._aliases,
                    description=description,
                    epilog=epilog,
                    help=description,
                )
                ec = child._configure_parser(subparser, self, stack)
                if ec:
                    return ec

        if not self._bare and not self._children:
            parser.set_defaults(**{STACK: stack})

    def _check_bare_arguments(self):
        if self._parent is not None:
            parser = self._parent._parser
            if parser._clik_bare_dests is not None:
                args = self._ctx.get(ARGS)
                for dest in parser._clik_bare_dests:
                    if getattr(args, dest) != parser.get_default(dest):
                        parser.print_usage(sys.stderr)
                        for action in parser._actions:  # pragma: no branch
                            if action.dest == dest:
                                break
                        else:  # pragma: no cover (unreachable)
                            raise Exception('this code should be unreachable')
                        options = '/'.join(action.option_strings)
                        err = 'unrecognized arguments when calling subcommand'
                        fmt = '%s: error: %s: %s'
                        msg = fmt % (parser.prog, err, options)
                        print(msg, file=sys.stderr)
                        return 1
                    delattr(args, dest)

    def _run(self, child=False):
        stack = getattr(self._ctx.get(ARGS), STACK)

        if not child:
            for command in stack:
                ec = command._check_bare_arguments()
                if ec:
                    return ec

        command = stack.pop(0)

        if stack:
            def run_children():
                return stack[0]._run(child=True)

            with self._ctx(run_children=run_children):
                try:
                    ec = next(command._generator)
                except StopIteration:
                    ec = 0
            if ec and ec is not catch:
                return ec

            if stack:
                if ec is catch:
                    ec = 0
                    exception = None
                    try:
                        ec = run_children()
                    except Exception as e:
                        exception = e
                    send = (ec, exception)
                else:
                    send = ec = run_children()
                try:
                    ec = command._generator.send(send)
                except StopIteration:
                    pass
        else:
            def run_children():
                return 0

            with self._ctx(run_children=run_children):
                try:
                    ec = next(command._generator)
                except StopIteration:
                    ec = 0

        return ec
