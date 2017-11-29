# -*- coding: utf-8 -*-
"""
Top-level :class:`App` class and helpers.

:author: Joe Joyce <joe@decafjoe.com>
:copyright: Copyright (c) Joe Joyce and contributors, 2009-2017.
:license: BSD
"""
import sys

from clik.argparse import ALLOW_UNKNOWN, ArgumentParser, ArgumentParserExit
from clik.command import Command
from clik.context import Context
from clik.magic import Magic
from clik.util import AttributeDict


#: Magic variable containing parsed arguments.
#:
#: :type: :class:`clik.magic.Magic` -- :class:`argparse.Namespace`
args = Magic('args')

#: Magic variable containing the active application instance.
#:
#: :type: :class:`clik.magic.Magic` -- :class:`clik.app.App`
current_app = Magic('current_app')

#: Magic variable containing globals.
#:
#: :type: :class:`clik.magic.Magic` -- :class:`clik.app.AttributeDict`
g = Magic('g')

#: Magic variable containing the current parser.
#:
#: :type: :class:`clik.magic.Magic` -- :class:`clik.argparse.ArgumentParser`
parser = Magic('parser')

#: Magic variable containing the function to run child commands.
#:
#: :type: :class:`clik.magic.Magic`
run_children = Magic('run_children')

#: Magic variable containing unknown arguments.
#:
#: :type: :class:`clik.magic.Magic` -- :class:`list`
unknown_args = Magic('unknown_args')


def app(fn=None, name=None):
    """
    Decorate the main application generator function.

    If the decorator is given no arguments, the name of the application is the
    name of the decorated generator function::

        # Application will be named 'myapp' in this case
        @app
        def myapp():
            yield

    The application name can be set by passing a string to ``name``::

        # Application will be named 'theapp' in this case
        @app(name='theapp')
        def myapp():
            yield

    :param fn: Main application generator function. Name of the application
               will be set to ``fn.__name__``.
    :param name: Overrides name of application. Must not be used with the
                 ``fn`` argument (if used with ``fn``, ``name`` is ignored).
    :return: :class:`App` if ``fn`` is ``None``, otherwise a decorator
             returning :class:`App`.
    """
    def decorate(fn):
        return App(fn, name)
    if fn is None:
        return decorate
    return decorate(fn)


class App(Command):
    """
    :class:`clik.Command` subclass that implements the :meth:`main` method.

    :meth:`main` is the user-level API for starting the application.
    """

    def __init__(self, fn, name=None):
        """
        Initialize the application object.

        :param fn: Main application generator function.
        :param name: Optional :class:`str` specifying the application name.
                     If not supplied the application name is set to
                     ``fn.__name__``.
        """
        super(App, self).__init__(Context(), fn, name=name)

    def main(self, argv=None, exit=sys.exit):
        """
        Start the application.

        :param argv: Optional list of command-line arguments. If not supplied,
                     this defaults to ``sys.argv``.
        :param exit: Optional function to call on exit. If not supplied,
                     this defaults to :func:`sys.exit`.
        :type exit: ``fn(integer_exit_code)``
        :return: Return value of ``exit``
        """
        if argv is None:  # pragma: no cover (hard to test, obviously correct)
            argv = sys.argv

        description, epilog = self._split_docstring(self._fn)
        root_parser = ArgumentParser(
            prog=self._name,
            description=description,
            epilog=epilog,
        )
        root_parser.set_defaults(**{ALLOW_UNKNOWN: False})

        magics = (args, current_app, g, parser, run_children, unknown_args)
        with self._ctx.acquire(*magics):
            with self._ctx(current_app=self, g=AttributeDict()):
                with self._ctx(args=None):
                    ec = self._configure_parser(root_parser)
                if ec:
                    return exit(ec)
                try:
                    known, unknown = root_parser.parse_known_args(argv[1:])
                except ArgumentParserExit:
                    return exit(1)
                if unknown and not getattr(known, ALLOW_UNKNOWN):
                    try:
                        root_parser.parse_args(argv[1:])
                    except ArgumentParserExit:
                        return exit(1)
                with self._ctx(args=known, unknown_args=unknown):
                    return exit(self._run())
