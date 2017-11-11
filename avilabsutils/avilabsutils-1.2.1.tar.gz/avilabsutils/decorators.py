from functools import wraps
import time
import logging


class MaxRetriesExceededError(Exception):
    pass


def retry(max_retries=3):
    def retry_dec(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    attempt += 1
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries:
                        time.sleep(attempt)
                    else:
                        errmsg = '{}() failed after {} retries'.format(func.__name__, max_retries)
                        raise MaxRetriesExceededError(errmsg) from e
        return wrapper
    return retry_dec


def debug(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        result = func(*args, **kwargs)
        args_str = [str(arg) for arg in args]
        kwargs_str = ['{}={}'.format(k, v) for k, v in kwargs.items()]
        all_args = args_str + kwargs_str
        all_params = ','.join([a for a in all_args])
        logger.debug('{}({}) = {}'.format(func.__name__, all_params, result))
        return result
    return wrapper


class InvalidArgError(Exception):
    pass


class InvalidArgTypeError(InvalidArgError):
    pass


class InvalidArgValueError(InvalidArgError):
    pass


# specs is an array of 3-value tuples -
# [(name, type, predicate), (name, type, predicate), ...)]
def validate_func_args(specs):
    args_specs = []
    kwargs_specs = {}
    for spec in specs:
        args_specs.append(spec[1:])
        kwargs_specs[spec[0]] = spec[1:]

    def validate_func_args_dec(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if len(args_specs) < len(args) or len(kwargs_specs) < len(kwargs):
                raise RuntimeError('All args do not have a spec')

            for i, arg in enumerate(args):
                arg_type = args_specs[i][0]
                if arg_type and not isinstance(arg, arg_type):
                    raise InvalidArgTypeError('Arg {} must be of type {}'.format(i, arg_type))

                arg_pred = args_specs[i][1]
                if arg_pred and not arg_pred(arg):
                    raise InvalidArgValueError('Arg {} has invalid value {}'.format(i, arg))

            for kwarg_name, kwarg in kwargs.items():
                kwarg_type = kwargs_specs[kwarg_name][0]
                if kwarg_type and not isinstance(kwarg, kwarg_type):
                    raise InvalidArgTypeError('Arg {} must be of type {}'.format(kwarg_name, kwarg_type))

                kwarg_pred = kwargs_specs[kwarg_name][1]
                if kwarg_pred and not kwarg_pred(kwarg):
                    raise InvalidArgValueError('Arg {} has invalid value {}'.format(kwarg_name, kwarg))

            return func(*args, **kwargs)

        return wrapper
    return validate_func_args_dec


def validate_method_args(specs):
    args_specs = []
    kwargs_specs = {}
    for spec in specs:
        args_specs.append(spec[1:])
        kwargs_specs[spec[0]] = spec[1:]

    def validate_method_args_dec(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            margs = args[1:]
            if len(args_specs) < len(margs) or len(kwargs_specs) < len(kwargs):
                raise RuntimeError('All args do not have a spec')

            for i, arg in enumerate(margs):
                arg_type = args_specs[i][0]
                if arg_type and not isinstance(arg, arg_type):
                    raise InvalidArgTypeError('Arg {} must be of type {}'.format(i, arg_type))

                arg_pred = args_specs[i][1]
                if arg_pred and not arg_pred(arg):
                    raise InvalidArgValueError('Arg {} has invalid value {}'.format(i, arg))

            for kwarg_name, kwarg in kwargs.items():
                kwarg_type = kwargs_specs[kwarg_name][0]
                if kwarg_type and not isinstance(kwarg, kwarg_type):
                    raise InvalidArgTypeError('Arg {} must be of type {}'.format(kwarg_name, kwarg_type))

                kwarg_pred = kwargs_specs[kwarg_name][1]
                if kwarg_pred and not kwarg_pred(kwarg):
                    raise InvalidArgValueError('Arg {} has invalid value {}'.format(kwarg_name, kwarg))
            return func(*args, **kwargs)

        return wrapper
    return validate_method_args_dec
