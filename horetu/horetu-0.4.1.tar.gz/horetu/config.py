import os
import re
import csv
import logging
from copy import copy
from io import StringIO
from collections import MutableMapping, OrderedDict, defaultdict

logger = logging.getLogger(__name__)

class Colon(csv.Dialect):
    delimiter = ':'
    doublequote = False
    escapechar = '\\'
    lineterminator = '\n'
    quotechar = None
    quoting = csv.QUOTE_NONE
    skipinitialspace = True
    strict = False

    @classmethod
    def reader(Class, fp):
        return csv.reader(fp, dialect=Class)

    @classmethod
    def writer(Class, fp):
        return csv.writer(fp, dialect=Class)

class Space(Colon):
    delimiter = ' '

    @classmethod
    def read(Class, strrow):
        x = strrow.rstrip(Class.lineterminator) + Class.lineterminator
        with StringIO(x) as fp:
            section = tuple(next(csv.reader(fp, dialect=Class)))
        return section

    @classmethod
    def write(Class, row):
        with StringIO() as fp:
            w = csv.writer(fp, dialect=Class)
            w.writerow(row)
            strrow = fp.getvalue().rstrip(Class.lineterminator)
        return strrow

class Configuration(OrderedDict):
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0:
            first_arg = args[0]
        else:
            first_arg = None

        if isinstance(first_arg, Configuration):
            self.update(first_arg)
        elif isinstance(first_arg, str):
            if os.path.isfile(first_arg):
                with open(first_arg) as fp:
                    self.update(Configuration.read_file(fp))
        elif hasattr(first_arg, 'read'):
            self.update(Configuration.read_file(first_arg))
        else:
            super(Configuration, self).__init__(*args, **kwargs)

    @staticmethod
    def _parse(key):
        if isinstance(key, str):
            return (key,)
        elif key == None or isinstance(key, tuple):
            return key
        else:
            raise KeyError(key)

    def __getitem__(self, key):
        try:
            value = super(Configuration, self).__getitem__(self._parse(key))
        except KeyError:
            value = Section()
            super(Configuration, self).__setitem__(self._parse(key), value)
        return value

    def __setitem__(self, key, value):
        if isinstance(value, Section):
            super(Configuration, self).__setitem__(self._parse(key), value)
        elif isinstance(value, dict):
            super(Configuration, self).__setitem__(self._parse(key), Section(value))
        else:
            raise ValueError('Not section type: %s' % repr(value))

    @classmethod
    def read_input(Class, section=None,
            positional=(), keyword1=(), var_positional=(), keyword2=()):
        '''
        :returns: The configuration
        :type section: Iterable of tuple of str, or None
        :param section: Subcommand to apply the configuration to, or
            None (default) to apply it to all subcommands
        :type positional: Iterable of tuple of str and anything
        :param positional: Positional arguments
        :param keyword1: Keyword arguments that came before a variable
            positional argument
        :type var_positional: Iterable of tuple of str and anything
        :param var_positional: Variable positional arguments (``*args``)
        :param keyword2: Other keyword arguments 
        :rtype: Configuration
        :returns: The configuration
        '''
        merged_inputs = list(positional + keyword1)
        if 1 == len(var_positional):
            name, values = var_positional[0]
            for value in values:
                merged_inputs.append((name, value))
        merged_inputs.extend(keyword2)

        c = Class()
        for key, value in merged_inputs:
            c[section].append(key, value)
        return c

    @classmethod
    def read_file(Class, source):
        '''
        :type source: str or file-like object with "r" mode
        :param source: Configuration file
        :rtype: Configuration
        :returns: The configuration
        '''
        if isinstance(source, str):
            fp = StringIO(source)
        elif hasattr(source, 'read'):
            fp = source
        else:
            raise TypeError('Unrecognized source: %s' % repr(source))
        rows = list(Colon.reader(fp))
        fp.close()
        lengths = set(map(len, rows))

        c = Class()
        if lengths == {2}:
            for argument, value in rows:
                c[None].append(argument, value)
        elif lengths == {3}:
            for section, argument, value in rows:
                c[Space.read(section)].append(argument, value)
        else:
            raise ValueError('Inconsistent formatting in DSV file')
        return c

    @classmethod
    def read_filename(Class, source):
        with open(source) as fp:
            c = Class.read_file(fp)
        return c

    def write(configuration, with_sections=True):
        '''
        :param Configuration configuration: The configuration values to write
        :param bool with_sections: Save different values for arguments of
            the same name in different sections
        :rtype: str
        :returns: Configuration file
        '''
        with StringIO() as fp:
            w = Colon.writer(fp)
            for section, s in configuration.items():
                for argument, values in s.items():
                    if with_sections:
                        left = Space.write(section),
                    else:
                        left = tuple()
                    for value in values:
                        w.writerow(left + (argument, value,))
            text = fp.getvalue()
        return text

    @classmethod
    def merge(Class, *configurations):
        '''
        :param Configuration configurations: The configurations to merge
        '''
        c = Class()
        for configuration in configurations:
            for section, s in configuration.items():
                for argument, value in s.items():
                    c[section][argument] = value
        return c

class ListArgument(list):
    pass

class Section(OrderedDict):
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and isinstance(args[0], Section):
            self.update(args[0])
        else:
            super(Section, self).__init__(*args, **kwargs)

    def flatten(self, defaults={}, list_type=tuple()):
        out = OrderedDict()

        # Apply configurations.
        for key, value in self.items():
            if key in list_type:
                if key not in out:
                    out[key] = ListArgument()
                out[key].extend(value)
            else:
                out[key] = value[-1]

        # Apply defaults.
        for key in defaults:
            if key not in out:
                out[key] = defaults[key]

        return out

    @staticmethod
    def _check(key):
        if not isinstance(key, str):
            raise KeyError('Not str type: %s' % key)

    def __getitem__(self, key):
        self._check(key)
        return super(Section, self).__getitem__(key)

    def __setitem__(self, key, values):
        self._check(key)
        if not isinstance(values, list) and all(isinstance(v, str) for v in values):
            raise TypeError('Argument values must be a list of str')
        return super(Section, self).__setitem__(key, values)

    def append(self, key, value):
        if isinstance(value, str):
            if not key in self:
                self[key] = []
            self[key].append(value)
        else:
            raise TypeError('Argument value must be str, not %s (key %s)' % \
                            (type(value), key))

    def extend(self, key, values):
        for value in values:
            self.append(key, value)
