import sys
import itertools
import textwrap
import shutil
import subprocess
from collections import OrderedDict
from triedict import triedict
from . import _util
from . import _bind
from .. import exceptions
from ..program import Program
from ..annotations import Flag

import os
XDG_OPEN = ('xdg-open', '/dev/stdin')

def cli(program, argv=sys.argv, return_=False,
        handlers=None, freedesktop=False,
        linebreak=True,
        exit_=sys.exit, stdout=sys.stdout.buffer, stderr=sys.stderr.buffer):
    '''
    :type program: Program, callable, list, or dict
    :param program: The program for which to produce the interface
    :param list argv: :py:obj:`sys.argv` by default
    :param bool return_: If this is ``True``, simply return the result of the function;
        do not write stuff to ``exit_``, ``stdout``, or ``stderr``.
    :param function exit_: :py:func:`sys.exit` by default
    :param dict handlers: Mapping from content type to handler program
    :param bool freedesktop: Fall back to xdg-open if a handler is not available
    :param bool linebreak: If the program returns an iterator, horetu will print
        string representations of the elements in the iterator. If this is True,
        horetu will add a newline character after each string element.
    :type stdout: Binary file
    :param stdout: :py:func:`sys.stdout.buffer` by default
    :type stderr: Binary file
    :param stderr: :py:func:`sys.stderr.buffer` by default
    '''
    if not handlers:
        handlers = {}
    argv = list(argv) # Prevent myself from modifying the input.
    if not isinstance(program, Program):
        program = Program(program)
    if not program.name:
        program.name = argv[0]

    def write(stream, fp):
        for line in stream:
            fp.write(line.encode('utf-8') + b'\n')
        fp.flush()

    if return_:
        section, raw_arguments = _bind.web_section(program, argv[1:])
        function = program[section]
        function.require_help()
        arguments = from_argv(function, raw_arguments)
        return function.run('raw', arguments)
    else:
        try:
            try:
                section, raw_arguments = _bind.cli_section(program, argv[1:])
                try:
                    function = program[section]
                    function.require_help()
                    arguments = from_argv(function, raw_arguments)

                    raw_output = function.run('raw', arguments)

                    rt = function.return_type
                    if rt and (freedesktop or (rt.parsed in handlers)):

                        handler = handlers.get(rt.parsed, XDG_OPEN)

                        if isinstance(raw_output, bytes):
                            stream = [raw_output]
                        else:
                            stream = raw_output
                        p = subprocess.Popen(handler, stdin=subprocess.PIPE, stderr=stderr)
                        for element in stream:
                            if isinstance(element, bytes):
                                p.stdin.write(element)
                            else:
                                raise ValueError('When you set a content type, the function must return either bytes or an iterable of bytes.')
                        p.stdin.close()
                        p.wait()
                    else:
                        suffix = b'\n' if linebreak else b''
                        for line in _util.stream(raw_output):
                            stdout.write(line + suffix)
                            stdout.flush()

                except exceptions.BaseHoretuException as e:
                    e.section = section
                    raise e

            except exceptions.ShowHelp as e:
                write(man(program, e), stdout)
                exit_(0)
            except exceptions.CouldNotParse as e:
                stdout.flush()
                write(usage(program, e), stderr)
                exit_(2)
            except exceptions.Error as e:
                stdout.flush()
                write(usage(program, e), stderr)
                exit_(3)
            else:
                exit_(0)
        except BrokenPipeError:
            stderr.close()

def from_argv(function, raw_arguments):
    mixed = iter(raw_arguments)
    keyword2_params = triedict({param.name: param for param in function.keyword2})

    positional = []
    keyword2 = []
    before_double_hyphen = True

    while True:
        try:
            raw_arg = next(mixed)
        except StopIteration:
            break

        arg = raw_arg[1:]
        if before_double_hyphen and raw_arg.startswith('-'):
            if raw_arg == '--':
                before_double_hyphen = False
            elif arg in keyword2_params:
                p = keyword2_params[arg]
                if isinstance(p, Flag):
                    value = Flag.YES
                else:
                    try:
                        value = next(mixed)
                    except StopIteration:
                        raise exceptions.CouldNotParse('Needs parameter -- %s' % arg)
                keyword2.append((p.name, value))
            else:
                raise exceptions.CouldNotParse('Unknown option -- %s' % arg)
        else:
            positional.append(raw_arg)

    arguments = _bind.positionals(function, positional)
    for name, value in keyword2:
        if not name in arguments:
            arguments[name] = []
        arguments[name].append(value)
    return arguments


def _section_prefix(prog, x):
    for section in sorted(prog, key=len, reverse=True):
        if tuple(section[:len(x)]) == x:
            return x
    return tuple()

def _endpoints(program, section):
    for subsection in program.subset(section):
        s = program[subsection]
        signature = ''
        for x in s.positional:
            signature += ' %s' % x.name
        for x in s.keyword1:
            signature += ' [%s]' % x.name
        if s.var_positional:
            signature += ' [%s ...]' % s.var_positional[0].name
        yield subsection, signature[1:]

def _join(f):
    def decorator(*args, **kwargs):
        return '\n'.join(f(*args, **kwargs))
    return decorator

@_join
def _format_arg(prefix, indent, param):
    columns, _ = shutil.get_terminal_size((80, 20))
    whitespace = ' ' * len(param.name)
    n = columns - len(param.name) - indent - len(prefix) - 2
    
    first = True
    for right in textwrap.wrap(param.description, n):
        if first:
            left = param.name + ': '
            first = False
        else:
            left = whitespace + '  '
        yield (' ' * indent) + left + right

def usage(prog, h):
    p = {
        'name': prog.name,
        'message': h.message,
        'endpoints': _endpoints(prog, h.section if h.section in prog else tuple()),
    }
    if p['message']:
        yield 'error: %(message)s' % p

    for i, (section, signature) in enumerate(p['endpoints']):
        yield _usage_line(prog, section, signature,
                          'usage: ' if i == 0 else '       ')

def _usage_line(program, section, signature, prefix):
    function = program[section]
    function.require_help()
    help_flag = function.help_flag()
    q = {
        'prefix': prefix,
        'name': program.name,
        'sub': (' ' + ' '.join(section)).rstrip() + ' ',
        'signature': signature,
        'sep': ' [--] ' if any(signature) else ' ',
        'help': ('[-%s] ' % help_flag) if help_flag else '',
    }
    return '%(prefix)s%(name)s%(sub)s%(help)s[options]%(sep)s%(signature)s' % q

def man(prog, h):
    columns, _ = shutil.get_terminal_size((80, 20))
    f = prog[h.section]
    p =  {
        'name': prog.name,
        'endpoints': _endpoints(prog, h.section),
        'description': f.description,
        'args': (_format_arg(' ', 2, a) for a in f.all_positionals()),
        'kwargs': (_format_arg('-', 2, a) for a in f.keyword2),
    }

    yield 'SYNOPSIS'
    for section, signature in p['endpoints']:
        yield _usage_line(prog, section, signature, '  ')
    if p['description']:
        yield 'DESCRIPTION'
        for line in textwrap.wrap(p['description'], columns-2):
            yield '  ' + line
    if p['args']:
        yield 'INPUTS'
        for arg in p['args']:
            yield arg
        try:
            arg
        except NameError:
            yield '  (None)'
    yield 'OPTIONS'
    for kwarg in p['kwargs']:
        yield kwarg
