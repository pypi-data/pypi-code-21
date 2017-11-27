import subprocess
from argparse import RawDescriptionHelpFormatter
from collections import ChainMap, OrderedDict
from triedict import triedict
from . import _bind
from . import _util
from ..annotations import Flag
from .. import exceptions
from ..program import Program

def django(program, handlers=None, freedesktop=False):
    '''
    Produce a django management command to be assigned to
    ``<project>.management.commands.Command``.

    :type program: Program, callable, list, or dict
    :param program: The program for which to produce the interface
    :param dict handlers: Mapping from content type to handler program
    :param bool freedesktop: Fall back to xdg-open if a handler is not available
    '''
    try:
        from django.core.management.base import BaseCommand, CommandError
    except ImportError:
        logger.error('Django is not installed; run this: pip install horetu[all]')
        sys.exit(1)

    if not handlers:
        handlers = {}

    if not isinstance(program, Program):
        program = Program(program)

    if set(program) == {()}:
        function = program[()]
    else:
        raise ValueError('Subcommands are not allowed in the argparse/django interface.')

    parser_hack = []
    class Command(BaseCommand):
        def add_arguments(self, parser):
            parser_hack.append(parser)
            parser.formatter_class=RawDescriptionHelpFormatter
            parser.description = function.description
            one(parser, function)

        def handle(self, *args, **options):
            if args != ():
                raise NotImplementedError('I don\'t know what to do with args.: ' + repr(args))
            inputs = parse_options(function, options)
            fp = self.stdout
            try:
                raw_output = function.run('raw', inputs)
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
                    for line in _util.stream(raw_output):
                        self.stdout.buffer.write(line + b'\n')
                        self.stdout.flush()
        #   except exceptions.CouldNotParse as e:
        #       parser_hack[0].error('')
            except exceptions.Error as e:
                raise CommandError(e.message)
            # It is a bug if other horetu exceptions are raised
    return Command

def parse_options(function, kwargs):
    arguments = OrderedDict()
    params = triedict({param.name: param for param in function.all_parameters()})
    for key, value in kwargs.items():
        if key in params:
            p = params[key]
            if isinstance(p, Flag):
                value = Flag.YES
            if not p.name in arguments:
                arguments[p.name] = []
            arguments[p.name].append(value)
    return arguments

def one(parser, f):
    def kw(param, **kwargs):
        def Type(x):
            return param.loads('raw', x)
        Type.__name__ = param.__name__
        kwargs.update({
            'type': Type,
            'default': param.default,
            'help': param.description,
        })
        if kwargs['action'] in {'store_true', 'store_false', 'count'}:
            del(kwargs['nargs'])
        return kwargs

    for param in f.positional:
        parser.add_argument(param.name, **kw(param, action='store'))
    for param in f.keyword1:
        parser.add_argument(param.name, **kw(param, nargs='?'))
    for param in f.var_positional:
        parser.add_argument(param.name, **kw(param, nargs='*', action='store'))
    for param in f.keyword2:
        if isinstance(param, Flag):
            action = 'store_true'
        elif param.is_list_type:
            action = 'append'
        else:
            action = 'store'
        parser.add_argument('--'+param.name, **kw(param, action=action))
