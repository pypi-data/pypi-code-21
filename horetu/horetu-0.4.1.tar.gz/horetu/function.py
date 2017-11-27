import logging
import inspect
import re
from collections import OrderedDict
from itertools import filterfalse, chain
from functools import partial
from enum import Enum
from .annotations import Help, Annotation
from .exceptions import CouldNotParse
from ._content_type import ContentType

logger = logging.getLogger(__name__)

class Function(object):
    def __init__(self, f, configured_defaults):
        '''
        :param dict configured_defaults: Defaults from program configuration
        '''
        self._function = f
        self._configured_defaults = configured_defaults or {}

        s = inspect.signature(f)
        for kind in Kind:
            setattr(self, kind.name, [])
        
        for kind, param in _kinds(s):
            getattr(self, kind.name).append(Annotation.bind(param))

        for param in self.all_parameters():
            _inspect_param = s.parameters[param.name]
            if _inspect_param.default != _inspect_param.empty:
                param.default = _inspect_param.default

        ps = {param.name: param for param in self.all_parameters()}
        doc_params, self.description = _doc(f)
        for name, desc in doc_params:
            if name in ps:
                ps[name].description = desc
            else:
                logger.warning('Docstring references non-variable "%s"' % name)

        if s.return_annotation in {s.empty, None}:
            self.return_type = None
        else:
            self.return_type = ContentType(s.return_annotation)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self._function)

    def all_positionals(self):
        return chain(*(getattr(self, kind.name) for kind in
                       [Kind.positional, Kind.keyword1, Kind.var_positional]))
    def all_parameters(self):
        return chain(*(getattr(self, kind.name) for kind in Kind))

    def help_flag(self):
        for param in self.keyword2:
            if isinstance(param, Help):
                return param.name

    def _manual_help_flag(self):
        s = inspect.signature(self._function)
        for param in s.parameters.values():
            if param.annotation == Help:
                return param.name

    def require_help(self):
        s = inspect.signature(self._function)
        if (Help.NAME not in s.parameters) and not self._manual_help_flag():
            class param:
                name = Help.NAME
                annotation = Help
                default = False
                empty = inspect.Parameter.empty
                kind = 'beep'
                VAR_POSITIONAL = 'boop'
            self.keyword2.append(Annotation.bind(param))

    @property
    def defaults(self):
        '''
        Assign defaults from the function signature.
        No parsing nor reshaping is needed.
        '''
        arguments = OrderedDict()
        for param in self.all_parameters():
            if param.default != inspect.Parameter.empty:
                arguments[param.name] = param.default 
        return arguments

    def run(self, loader, raw_arguments):
        '''
        :param loader: "raw", "wsgi", or "gtk"
        :type raw_arguments: dict of str to list of unparsed values
        :param raw_arguments: Arguments of function call
        '''
        arguments = {}

        # Parse inputs, convert list-typed status, and assign
        for param in self.all_parameters():
            def _parse(arg):
                f = partial(param.loads, loader)
                try:
                    if param.is_list_type:
                        return param.finalize_list(list(map(f, arg)))
                    else:
                        return f(arg[-1])
                except ValueError as e:
                    raise CouldNotParse('Could not parse %s: %s' % (param.name, e))

            if isinstance(param, Help):
                if raw_arguments.get(param.name,
                        self._configured_defaults.get(param.name,
                            self.defaults[param.name])):
                    param.loads(loader, True)
            elif param.name in raw_arguments:
                arguments[param.name] = _parse(raw_arguments[param.name])
            elif param.name in self._configured_defaults:
                arguments[param.name] = _parse(self._configured_defaults[param.name])
            elif param.name in self.defaults:
                arguments[param.name] = self.defaults[param.name]

        # Checks
        for param in self.positional:
            if param.name not in arguments:
                raise CouldNotParse('Missing positional argument: %s' % param.name)

        # Represent as args and kwargs
        args = []
        kwargs = {}

        for param in self.positional + self.keyword1 + self.var_positional:
            include = {True: args.extend, False: args.append}[param.is_list_type]
            if param.name in arguments:
                include(arguments[param.name])

        for param in self.keyword2:
            if param.name in arguments:
                if param.is_list_type:
                    kwargs[param.name] = list(arguments[param.name])
                else:
                    kwargs[param.name] = arguments[param.name]

        # Run
        return self._function(*args, **kwargs)


COLON = re.compile(r'^[\s:]')
def _colon(line):
    return bool(re.match(COLON, line))

def _desc(lines):
    return '\n'.join(filterfalse(_colon, lines)).strip()

PARAM = re.compile(r'^:param (?:[^:]+ )?([^:]+): (.+)$')
INDENT = re.compile(r'\s+([^\s].*)')

def _doc(function):
    d = inspect.getdoc(function)
    if d:
        lines = d.split('\n')
    else:
        lines = []

    y = []
    z = ''

    name = None
    for line in lines:
        if _colon(line):
            m = re.match(PARAM, line)
            n = re.match(INDENT, line)
            if m:
                # New parameter
                if name:
                    # Save the previous parameter if it exists.
                    y.append((name, desc.strip()))
                    name = None

                # Start the new description
                name, desc = m.groups()
            elif name and n:
                desc += ' ' + n.group(1)
        else:
            z += line

    if name:
        # Save the last parameter
        y.append((name, desc.strip()))
    
    return y, z

class Kind(Enum):
    positional = 1
    keyword1 = 2
    var_positional = 3
    keyword2 = 4

    # https://docs.python.org/3/library/enum.html#orderedenum
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        else:
            return NotImplemented
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        else:
            return NotImplemented
    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        else:
            return NotImplemented
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        else:
            return NotImplemented

KINDS = {
    Kind.positional: {
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD
    },
    Kind.keyword1: {inspect.Parameter.POSITIONAL_OR_KEYWORD},
    Kind.var_positional: {inspect.Parameter.VAR_POSITIONAL},
    Kind.keyword2: {inspect.Parameter.KEYWORD_ONLY},
}

def _kinds(sig):
    has_k2 = Kind.keyword2 in (k for k,_ in _naive_kinds(sig))
    for kind, param in _naive_kinds(sig):
        if kind == Kind.keyword1 and not has_k2:
            yield Kind.keyword2, param
        else:
            yield kind, param

def _naive_kinds(sig):
    for param in sig.parameters.values():
        if param.kind in KINDS[Kind.positional].union(KINDS[Kind.keyword1]):
            if param.default == param.empty:
                kind = Kind.positional
            else:
                kind = Kind.keyword1
        elif param.kind in KINDS[Kind.var_positional]:
            kind = Kind.var_positional
        elif param.kind in KINDS[Kind.keyword2]:
            kind = Kind.keyword2
        yield kind, param
