from functools import wraps
from py_type.output import output
from py_type.checks import check_set, message, check_list


class Signature:
    def __init__(self):
        pass

    @staticmethod
    def check_args(args=None, arg_types=None):
        print('args: ' + str(args))
        types = map(type, args)
        check_list(arg_types, types)

    @staticmethod
    def check_kwargs(kwargs=None, kwarg_types=None):
        print('kwargs:' + str(kwargs))
        ks = kwargs.keys()
        check_set(ks, kwarg_types.keys())
        bs = map(lambda k: type(kwargs[k])==kwarg_types[k], ks)
        if not all(bs):
            output.error_func(message(kwarg_types, kwargs))

    @staticmethod
    def check(level='all', args=None, arg_types=None, kwargs=None, kwarg_types=None):
        if output.do_check(level):
            if arg_types is not None:
                Signature.check_args(args, arg_types)
            if kwarg_types is not None:
                Signature.check_kwargs(kwargs, kwarg_types)

    @staticmethod
    def input(level='all', arg_types=None, kwarg_types = None):
        def decorator(f):
            @wraps(f)
            def _f(*args, **kwargs):
                Signature.check(level, args, arg_types, kwargs, kwarg_types)
                return f(*args, **kwargs)
            return _f
        return decorator

        
class Pandas:
    def __init__(self):
        pass

    debug = False

    @staticmethod
    def check_column_names(df, column_names):
        check_set(df.columns.values, column_names)

    @staticmethod
    def check_index_names(df, index_names):
        check_set(df.index.names, index_names)

    @staticmethod
    def check_column_types(df, column_types):
        ks = column_types.keys()
        exps = [column_types[k] for k in ks]
        gots = [df[k].dtype for k in ks]
        bs = map(lambda exp, got: exp == got, exps, gots)
        if not all(bs):
            output.error_func('expected: ' + str(exps) + ', got: ' + str(gots))

    @staticmethod
    def check(df, level='all', column_names=None, index_names=None, column_types=None):
        if output.do_check(level):
            if column_names is not None:
                Pandas.check_column_names(df, column_names)
            if index_names is not None:
                Pandas.check_index_names(df, index_names)
            if column_types is not None:
                Pandas.check_column_types(df, column_types)

    @staticmethod
    def input(level='all', arg_pos=0, column_names=None, index_names=None, column_types=None):
        def decorator(f):
            @wraps(f)
            def _f(*args, **kwargs):
                df = args[arg_pos]
                Pandas.check(df, level, column_names, index_names, column_types)
                return f(*args, **kwargs)
            return _f
        return decorator

    @staticmethod
    def output(level='all', out_pos=0, column_names=None, index_names=None, column_types=None):
        def decorator(f):
            @wraps(f)
            def _f(*args, **kwargs):
                df = f(*args, **kwargs)
                Pandas.check(df, level, column_names, index_names, column_types)
                return df
            return _f
        return decorator

        