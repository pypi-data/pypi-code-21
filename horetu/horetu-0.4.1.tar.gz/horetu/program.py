import logging
from inspect import getmembers
from copy import copy
from itertools import chain
from triedict import triedict
from collections import Mapping
from .function import Function
from .config import Configuration
logger = logging.getLogger(__name__)

class Program(Mapping):
    def __init__(self, function, *configurations, name=None):
        '''
        :param functions: Base function or functions
        :param Configuration configurations: Configuration files and other
            configuration sources
        :param name: Force the program to have a particular name.
        '''
        if name is None and hasattr(function, '__call__'):
            name = function.__name__
        self.name = name
        self._function = function
        self._configurations = tuple(map(Configuration, configurations))
        self._d = triedict(_sub(tuple(), function))

    def subset(self, prefix):
        for section, function in self.items():
            if section[:len(prefix)] == prefix:
                yield section

    def __repr__(self):
        tpl = '%(class)s(%(function)s, %(configuration)s, name=%(name)s)'
        return tpl % {
            'class': self.__class__.__name__,
            'function': getattr(self._function, '__name__', repr(self._function)),
            'configuration': repr(self.configuration()),
            'name': repr(self.name),
        }

    def configuration(self):
        return Configuration.merge(*self._configurations)

    def __getitem__(self, section):
        c = self.configuration()
        defaults = {}
        for name, value in chain(c[None].items(), c.get(section, {}).items()):
            defaults[name] = value
        return Function(self._d[section], defaults)

    def __copy__(self):
        return Program(self._function, *self._configurations, name=self.name)

    def __iter__(self):
        for section, function in self._d.items():
            if callable(function):
                yield section

    def __len__(self):
        return len(self._d)

def _sub(section, fs):
    '''
    :param tuple section: Sections that this sub-program is under
    '''
    if hasattr(fs, 'items'):
        items = fs.items()
    elif hasattr(fs, '__iter__'):
        gs = list(fs)
        if all(hasattr(g, '__name__') for g in gs):
            items = ((g.__name__, g) for g in gs)
        else:
            raise TypeError('Bad function component: %s' % repr(fs))
    elif hasattr(fs, '__call__'):
        yield section, fs
        if isinstance(fs, type):
            items = (item for item in getmembers(fs) \
                     if not item[0].startswith('_'))
        else:
            items = []
    else:
        raise TypeError('Bad function component: %s' % repr(fs))

    for name, f in items:
        _validate_param_name(*name)
        yield from _sub(section + (name,), f)

def _validate_param_name(*xs):
    msg = 'It is best if you remove "%s" from the argument name "%s".'
    for x in xs:
        for c in '/?[]<>():':
            if x in c:
                logger.warning(msg % (c, x))
