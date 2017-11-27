'''
Everything is string type, even if this is inefficient.

Class.loads always takes str input, and Class.dumps always
returns str output.
'''
import logging
import os
import io
import datetime
import base64
import re
from collections import OrderedDict, Hashable
from xml.etree import ElementTree as E
from functools import wraps
from abc import ABCMeta
from pprint import pformat
from . import exceptions

# Just for checking types
import decimal, inspect

logger = logging.getLogger(__name__)

UNDOCUMENTED = 'Undocumented'

_default_true = 'bool arguments must have default of False; consider changing param %(name)s to no%(name)s'

class AnnotationFactory(object):
    def __init__(self, Class, *args, **kwargs):
        self._Class = Class
        self._args = args
        self._kwargs = kwargs
    def __call__(self):
        try:
            return self._Class(*self._args, **self._kwargs)
        except ValueError:
            raise exceptions.CouldNotParse

class Annotation(object, metaclass=ABCMeta):
    allow_get = True
    def __init__(self, *args, **kwargs):
        raise NotImplementedError
    @staticmethod
    def finalize_list(xs):
        return xs

    def loads(self, loader, data):
        return {
            'raw': self._loads_raw,
            'wsgi': self._loads_wsgi,
            'urwid': self._loads_urwid,
        }[loader](data)
    def dumps(self, dumper, value):
        return {
            'raw': self._dumps_raw,
            'wsgi': self._dumps_wsgi,
            'urwid': self._dumps_urwid,
        }[dumper](value)

    def _label(self, tree, lines='one'):
        parent = E.Element('div', **{'class': 'list-box-row %sline' % lines})

        label = E.Element('label', **{
            'for': self.name,
            'title': self.description,
        })
        label.text = self.name

        parent.append(label)
        parent.append(tree)
        return parent

    #: Default documentation string
    description = UNDOCUMENTED
    default = inspect.Parameter.empty

    @classmethod
    def factory(Class, *args, **kwargs):
        return AnnotationFactory(Class, *args, **kwargs)

    @classmethod
    def bind(Class, param, _annotation=None):
        '''
        Bind an annotation to a parameter.

        :param inspect.Parameter param: Parameter from the function signature
        :param _annotation: Annotation for the resulting object instead
            of param.annotation, used only internally for recursion
        :ivar bool is_list_type: Whether the parameter takes multiple arguments
        :ivar default: Default value for keyword arguments (used for
            generating default configuration files)
        '''
        if _annotation:
            a = _annotation
        else:
            a = param.annotation

        if      (
                    (a == bool) or \
                    (a == param.empty and 
                        isinstance(param.default, bool) and
                        param.default==True)
                ) and \
                (not isinstance(param.annotation, list)) and \
                (param.default != False):
            raise ValueError(_default_true % {'name': param.name})
        elif isinstance(a, Class):
            raise TypeError('Annotations must be Annotation subclasses, not instances.')
        elif isinstance(a, type) and issubclass(a, Annotation):
            obj = a() # This works, of course, for only Annotations that accept no arguments.
        elif isinstance(a, AnnotationFactory):
            obj = a()
        elif a == inspect.Parameter.empty and \
                isinstance(param.default, bool) and param.default == False:
            obj = Boolean()
        elif isinstance(a, list) and len(a) == 1:
            if isinstance(a[0], list) and len(a[0]) == 1:
                raise ValueError('You can\'t nest list annotations.')
            obj = Class.bind(param, _annotation=a[0])
        elif _is_hashable(a) and a in annotations_map:
            obj = annotations_map[a]()
        elif hasattr(a, 'loads') and hasattr(a, 'dumps') \
            or hasattr(a, 'load') and hasattr(a, 'dump'):
            obj = Encoder(a)
        elif hasattr(a, '__call__'):
            obj = String(a)
        elif hasattr(a, 'items'):
            obj = FactorMapping(a)
        elif isinstance(a, tuple):
            obj = Factor(a)
        else:
            raise ValueError('Bad input annotation: %s' % x)

        if hasattr(obj, '__name__'):
            pass
        elif hasattr(a, '__name__'):
            obj.__name__ = a.__name__
        else:
            obj.__name__ = obj.__class__.__name__

        obj.name = param.name
        obj.default = param.default
        obj.is_list_type = (param.kind == param.VAR_POSITIONAL) or \
            (isinstance(a, list) and len(a) == 1)

        return obj

    def _loads_raw(self, data):
        raise AnnotationNotImplemented
    def _dumps_raw(self, value):
        raise AnnotationNotImplemented

    def _loads_wsgi(self, data):
        return self._loads_raw(data)
    def _dumps_wsgi(self, value):
        raise AnnotationNotImplemented
    
    def _loads_urwid(self, data):
        return self._loads_raw(data)
    def _dumps_urwid(self, value):
        raise AnnotationNotImplemented

    def __str__(self):
        return '<%s: %s>' % (self.name, self.__name__)

    YES = 'yes'
    NO = 'no'

def _is_hashable(x):
    '''
    I implemented this because ``isinstance({}.__getitem__, collections.Hashable)``
    does not do what I want.
    '''
    try:
        hash(x)
    except TypeError:
        return False
    else:
        return True

def _d(f):
    def wrapper(x):
        if x != inspect.Parameter.empty:
            try:
                return f('raw', x)
            except Exception:
                logger.exception('Error in dumping to web form')
        return ''
    return wrapper

class Encoder(Annotation, metaclass=ABCMeta):
    def __init__(self, x):
        if hasattr(x, 'loads') and hasattr(x, 'dumps'):
            self._loads_raw = x.loads
            self._dumps_raw = x.dumps
        elif hasattr(x, 'load') and hasattr(x, 'dump'):
            IO = {str: io.StringIO, bytes: io.BytesIO}[self._type]

            def _loads_raw(text):
                with IO(text) as fp:
                    obj = load(fp)
                return obj
            self._loads_raw = _loads_raw

            def _dumps_raw(obj):
                with IO() as fp:
                    dump(obj, fp)
                    text = fp.getvalue()
                return text
            self._dumps_raw = _dumps_raw
        else:
            raise TypeError('Not an encoder: %s' % x)
        self._x = x # just for repr
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self._x)

    def _dumps_wsgi(self, value):
        '''
        :param param: The parameter
        :param value: The default value
        '''
        tree = E.Element('textarea', name=self.name)
        if value:
            tree.text = _d(self.dumps)(value)
        return self._label(tree, lines='multi')

# Flags
class Flag(Annotation):
    def __init__(self, loads):
        self._loads_raw = loads
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self._loads_raw)

    def _loads_raw(self, yes=True):
        if yes in {self.YES, True}:
            self._loads()
            return True
        else:
            return False
    def _dumps_raw(self, yes):
        return self.YES if yes else self.NO

    def _dumps_wsgi(self, yes):
        attr = {'type': 'checkbox', 'name': self.name}
        if yes:
            attr['checked'] = self.YES
        input_ = E.Element('input', **attr)
        return self._label(input_)

@Flag.factory
def Boolean(_=None):
    return True
class Count(Flag):
    def __init__(self):
        super(Count, self).__init__(lambda _=None: True)
    finalize_list = len

class Help(Flag):
    NAME = 'help'
    __name__ = 'Help'
    def __init__(self):
        pass

    def __repr__(self):
        return '%s()' % self.__class__.__name__

    description = 'Display this help.'
    default = False

    def _loads_raw(self, _):
        raise exceptions.ShowHelp

# String types
class Text(Annotation, metaclass=ABCMeta):
    def _dumps_wsgi(self, value):
        attr = {'type': 'text', 'name': self.name}
        if value:
            attr['value'] = _d(self.dumps)(value)
        input_ = E.Element('input', **attr)
        return self._label(input_)

class Identity(Text):
    def __init__(self, type=str):
        self._type = type
    def __repr__(self):
        return '%s(type=%s)' % (self.__class__.__name__, self._type)

    def _check_type(self, x):
        if self._type and not isinstance(x, self._type):
            p = (self._type, type(x), repr(x))
            raise TypeError('Value must be %s, not %s: %s' % p)
        else:
            self._assign_type(x)
    def _assign_type(self, x):
        if not self._type:
            self._type = type(x)

    def _loads_raw(self, data):
        self._check_type(data)
        return data
    def _dumps_raw(self, value):
        self._check_type(value)
        return value

class Config(Identity):
    def __init__(self, filename):
        self._default_filename = filename
        super(Config, self).__init__(type=str)
    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.default_filename)

    def _loads_raw(self, _):
        raise exceptions.Config(self._default_filename)
    def _loads_wsgi(self, data):
        raise ValueError('Do not use the Config annotation for websites.')
    def _dumps_wsgi(self, obj):
        raise ValueError('Do not use the Config annotation for websites.')

class String(Text):
    def __init__(self, loads=lambda x: x):
        self.__name__ = loads.__name__
        self._loads_raw = loads
        self._dumps_raw = str
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self._loads_raw.__name__)

class Regex(Text):
    def __init__(self, expr):
        def loads(x):
            if re.match(expr, x):
                return x
            else:
                raise ValueError('Does not match regular expression: %s' % expr)

        self._expr = re.compile(expr)
        self.__name__ = '<Regex %s>' % self._expr
        self._loads_raw = loads
        self._dumps_raw = str
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self._expr)

class Bytes(Text):
    def __init__(self, loads=lambda x: x, dumps=lambda x: x, encoding='ascii'):
        decode, encode = _coders(encoding)

        self._loads_raw = lambda x: loads(encode(x))
        self._dumps_raw = lambda x: decode(dumps(x))

        # Just for repr
        self._loads = loads
        self._dumps = dumps
        self._encoding = encoding
    def __repr__(self):
        return '%s(loads=%s, dumps=%s, encoding=%r)' % \
            (self.__class__.__name__, self._loads, self._dumps, self._encoding)

def _coders(encoding):
    if isinstance(encoding, str):
        loads = lambda x: bytes.decode(x, encoding)
        dumps = lambda x: str.encode(x, encoding)
    elif encoding == None:
        loads = bytes.decode
        dumps = str.encode
    else:
        raise TypeError('Must be None or str, not %s' % type(encoding))
    return loads, dumps

@String.factory
def InputDirectory(x):
    if os.path.isdir(x):
        return x
    else:
        raise ValueError('No such directory: ' + str(x))

@String.factory
def OutputDirectory(x):
    os.makedirs(x, exist_ok=True)
    return x

@String.factory
def Port(x):
    y = int(x)
    if 1 <= y <= 65535:
        return y
    else:
        raise ValueError('Not a valid port number: %d' % y)

Decimal = String.factory(decimal.Decimal)
Integer = String.factory(int)
Float = String.factory(float)

class Range(String):
    def __init__(self, minimum, maximum, loads=float, dumps=str, step='any'):
        self._loads_raw = loads
        self._dumps_raw = dumps
        self._min = minimum
        self._max = maximum
        self._step = step
    def __repr__(self):
        return '%s(%r, %r, loads=%s, dumps=%s, step=%r)' % \
            (
                self.__class__.name, self._min, self._max,
                self._loads_raw, self._dumps_raw, self._step,
            )
        
    def _dumps_wsgi(self, name, default):
        '''
        :param name: The parameter name
        :param default: The default value, ignored
        '''
        attr = {
            'type': 'range', 'name': name,
            'min': _d(self.dumps)(self._min), 'max': _d(self.dumps)(self._min),
            'step': self._step if isinstance(self._step, str) else _d(self.dumps)(self._step),
        }
        if default:
            attr['value'] = _d(self.dumps)(default)
        input_ = E.Element('input', **attr)
        return self._label(input_)

# Factor types
class FactorMapping(String):
    def __init__(self, options):
        if not hasattr(options, 'items'):
            raise ValueError('Options must be dict-like')
        if not all(isinstance(option, str) for option in options):
            raise ValueError('All options must be of str type.')
        self._options = options

    def _reverse_options(self, value):
        xs = list(k for (k,v) in self._options.items() if v == value)
        if 0 == len(xs):
            raise ValueError('Must be one of %s' % repr(tuple(xs)))
        else:
            if 1 < len(xs):
                logger.warning('Multiple keys for %s, using the first' % repr(y))
                return next(xs)
            else:
                return xs[0]

    def _loads_raw(self, key):
        if key in self._options:
            return self._options[key]
        else:
            raise ValueError('Must be one of %s' % repr(tuple(self._options)))

    def _dumps_raw(self, value):
        return self._reverse_options(value)

    def _dumps_wsgi(self, selected):
        select = E.Element('select', name=self.name)
        if self.is_list_type:
            select.set('multiple', self.YES)
        else:
            selected = {selected}

        for value, text in self._options.items():
            option = E.Element('option', value=value)
            option.text = text
            if value in selected:
                option.set('selected', self.YES)
            select.append(option)

        return self._label(select)

class Factor(FactorMapping):
    def __init__(self, options):
        super(Factor, self).__init__(OrderedDict([(o,o) for o in options]))

# File pointer types
class File(Annotation):
    allow_get = False
    def __init__(self, mode, encoding=None, **kwargs):
        self._mode = mode
        self._decode, self._encode = _coders(encoding)
        self._encoding = encoding
        self._kwargs=kwargs

    def _loads_raw(self, filename):
        if 'r' in self._mode and not os.path.isfile(filename):
            raise ValueError('No such file: %s' % filename)
        return open(filename, mode=self._mode, encoding=self._encoding, **self._kwargs)

    def _dumps_raw(self):
        return self.fp.name

    def _loads_wsgi(self, data):
        if 'b' in self._mode:
            return data.file
        else:
            return io.StringIO(self._decode(data.file.read()))

    def _dumps_wsgi(self, default):
        '''
        :param name: The parameter name
        :param default: The default value, ignored
        '''
        attr = {'type': 'file', 'name': self.name, 'size': '40'}
        input_ = E.Element('input', **attr)
        return self._label(input_)

InputFile = File.factory('r')
InputBinaryFile = File.factory('rb')
OutputFile = File.factory('w')
OutputBinaryFile = File.factory('wb')

annotations_map = {
    bool: Boolean,
    bytes: Bytes,
    decimal.Decimal: Decimal, 'Decimal': Decimal,
    float: Float,
    inspect.Parameter.empty: Identity,
    int: Integer,
    str: Identity,

    'Help': Help,
    'Count': Count,

    'Config': Config,
    'Port': Port,
    'Range': Range,

    'InputFile': InputFile,
    'InputBinaryFile': InputBinaryFile,
    'OutputFile': OutputFile,
    'OutputBinaryFile': OutputBinaryFile,
}
