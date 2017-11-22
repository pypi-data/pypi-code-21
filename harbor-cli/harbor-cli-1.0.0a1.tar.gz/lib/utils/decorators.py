'''
A module for helpful decorators.
'''
import os
from functools import wraps

from lib.exceptions.FileNotFound import FileNotFoundException
from lib.exceptions.DirNotFound import DirNotFoundException

def requires_presence_of_file(file_path, on_failure=lambda *args: None):
    ''' Decorator to verify if a file exists before doing anything else. '''
    def wrapper(wrapped_func):
        ''' Take in the function, since the wrapper takes the args.'''
        @wraps(wrapped_func)
        def with_args(*args, **kwargs):
            ''' The innermost function that is returned by the decorator. '''
            if not os.path.isfile(file_path):
                raise FileNotFoundException(file_path, on_failure(file_path))

            return wrapped_func(*args, **kwargs)
        return with_args
    return wrapper


def requires_presence_of_dir(dir_path, on_failure=lambda *args: None):
    ''' Decorator to verify if a file exists before doing anything else. '''
    def wrapper(wrapped_func):
        ''' Take in the function, since the wrapper takes the args.'''
        @wraps(wrapped_func)
        def with_args(*args, **kwargs):
            ''' Returned function. '''
            if not os.path.isdir(dir_path):
                raise DirNotFoundException(dir_path, on_failure(dir_path))

            return wrapped_func(*args, **kwargs)
        return with_args
    return wrapper


def with_additional_kwargs(**additional_kwargs):
    '''
    Injects additional kwargs into the kwargs of the original func.
    Useful for injecting credentials/sensitive information into the function.
    '''
    def wrapper(wrapped_func):
        ''' Take in the function, since the wrapper takes the kwargs.'''
        @wraps(wrapped_func)
        def inner(*args, **kwargs):
            ''' Returned function. '''
            kwargs.update(additional_kwargs)
            return wrapped_func(*args, **kwargs)
        return inner
    return wrapper
