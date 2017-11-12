
from __future__ import absolute_import

import sys
import inspect
from collections import OrderedDict
import attr

is_py3 = sys.version_info.major >= 3
inspect_iscoroutinefunction = getattr(
    inspect, 'iscoroutinefunction', lambda f: False)


class temporal_property(object):
    '''Assiginable property'''

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, obj, cls):
        return self.getter(obj)


@attr.s
class Argument(object):
    _prefix = ''
    callable = attr.ib()
    position = attr.ib()
    index = attr.ib()

    @property
    def varname(self):
        return self.callable.code.co_varnames[self.index]

    @property
    def has_default(self):
        raise NotImplementedError  # pragma: no cover

    @property
    def has_annotation(self):
        return self.varname in self.callable.annotations

    @property
    def annotation(self):
        return self.callable.annotations[self.varname]


class PositionalArgument(Argument):

    @property
    def has_default(self):
        boundary = self.callable.code.co_argcount - len(self.callable.defaults)
        return boundary <= self.index

    @property
    def default(self):
        boundary = self.callable.code.co_argcount - len(self.callable.defaults)
        def_idx = self.index - boundary
        return self.callable.defaults[def_idx]


class KeywordOnlyArgument(Argument):
    @property
    def has_default(self):
        return self.varname in self.callable.kwdefaults

    @property
    def default(self):
        return self.callable.kwdefaults[self.varname]


class StarArgument(PositionalArgument):
    _prefix = '*'

    @property
    def has_default(self):
        return False


class DoubleStarArgument(PositionalArgument):
    _prefix = '**'

    @property
    def has_default(self):
        return False


class ArgumentList(list):

    @temporal_property
    def _table(self):
        self._table = {arg.varname: arg for arg in self}
        return self._table

    def get(self, varname):
        return self._table[varname]

    def keys(self):
        return self._table.keys()

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.get(item)
        return super(ArgumentList, self).__getitem__(item)


class Callable(object):

    def __init__(self, f):
        self.callable = f
        self.is_wrapped_coroutine = getattr(f, '_is_coroutine', None)
        self.is_coroutine = self.is_wrapped_coroutine or \
            inspect_iscoroutinefunction(f)
        self.decompose()

    def decompose(self):
        self.positional_arguments = ArgumentList()
        self.keyword_only_arguments = ArgumentList()
        self.star_argument = None
        self.double_star_argument = None

        code = self.code

        var_idx = 0
        for var_idx in range(code.co_argcount):
            argument = PositionalArgument(self, var_idx, var_idx)
            self.positional_arguments.append(argument)

        has_sarg = code.co_flags & 4
        pos_sarg = var_idx
        has_ssarg = code.co_flags & 8
        kwonlyargcount = getattr(code, 'co_kwonlyargcount', 0)

        for var_idx in range(var_idx + 1, var_idx + 1 + kwonlyargcount):
            argument = KeywordOnlyArgument(
                self, bool(has_sarg) + var_idx, var_idx)
            self.keyword_only_arguments.append(argument)

        if has_sarg:
            var_idx += 1
            self.star_argument = StarArgument(self, pos_sarg, var_idx)

        if has_ssarg:
            var_idx += 1
            self.double_star_argument = DoubleStarArgument(
                self, var_idx, var_idx)

    def iter_arguments(self):
        for arg in self.positional_arguments:
            yield arg
        if self.star_argument:
            yield self.star_argument
        for arg in self.keyword_only_arguments:
            yield arg
        if self.double_star_argument:
            yield self.double_star_argument

    @temporal_property
    def arguments(self):
        arguments = ArgumentList(self.iter_arguments())
        self.arguments = arguments
        return arguments

    @temporal_property
    def code(self):
        '''REAL __code__ for the given callable'''
        c = self.callable
        if self.is_wrapped_coroutine:
            code = c.__wrapped__.__code__
        else:
            code = c.__code__
        self.code = code
        return code

    @property
    def defaults(self):
        if self.is_wrapped_coroutine:
            c = self.callable.__wrapped__
        else:
            c = self.callable
        return getattr(c, '__defaults__', None) or ()

    @property
    def kwdefaults(self):
        return getattr(self.callable, '__kwdefaults__', None) or {}

    @property
    def annotations(self):
        return getattr(self.callable, '__annotations__', None) or {}

    def kwargify(self, args, kwargs):
        kwargs = kwargs.copy()
        code = self.code
        if len(args) > code.co_argcount and not self.star_argument:
            raise TypeError(
                '{}() takes {} positional arguments but {} were given'.format(
                    code.co_name, code.co_argcount, len(args)))
        merged = OrderedDict(
            (self.arguments[i].varname, arg)
            for i, arg in enumerate(args[:len(self.positional_arguments)]))
        i = len(merged)
        while i < len(self.positional_arguments):
            argument = self.positional_arguments[i]
            if argument.varname in kwargs:
                merged[argument.varname] = kwargs.pop(argument.varname)
            elif argument.has_default:
                merged[argument.varname] = argument.default
            else:
                missing_count = len(self.positional_arguments) - i
                raise TypeError(
                    "{}() missing {} required positional argument: '{}'".format(
                        code.co_name, missing_count, ', '.join(
                            '{arg.varname}'.format(arg=arg)
                            for arg in self.positional_arguments[i:i + missing_count])))
            i += 1

        if self.star_argument:
            merged[self.star_argument.varname] = args[i:]

        unhandled_kws = []
        for kw, arg in kwargs.items():
            if kw in merged:
                raise TypeError(
                    "{}() got multiple values for argument '{}'".format(
                        code.co_name, kw))
            elif kw in self.arguments.keys():
                merged[kw] = arg
            else:
                unhandled_kws.append(kw)

        for argument in self.keyword_only_arguments:
            if argument.varname in merged:
                continue
            if not argument.has_default:
                raise TypeError(
                    "{}() missing 1 required keyword-only argument: '{}'".format(
                        code.co_name, argument.varname))
            merged[argument.varname] = argument.default

        if self.double_star_argument:
            merged[self.double_star_argument.varname] = {
                kw: kwargs[kw] for kw in unhandled_kws}

        return merged
