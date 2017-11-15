# """ Config utility class """
# from functools import getfullargspec
# import json

# def with_config(func):
#     """ Add support to read keywargs from JSON file

#     Add a preserved keyword `config_filenames` for JSON file names to read.
#     """
#     @wraps(func)
#     def wrapper(*args, config_filenames=None, **kwargs):
#         if isinstance(config_filenames, str):
#             config_filenames = [config_filenames]
#         if config_filenames is None:
#             config_filenames = []
#         paras = getfullargspec(func)
#         json_dicts = []
#         for fn in config_filenames:
#             with open(fn, 'r') as fin:
#                 json_dicts.append(json.load(fin))
#         if paras.defaults is not None:
#             nb_def = len(paras.defaults)
#         else:
#             nb_def = 0
#         def_args = paras.defaults
#         if def_args is None:
#             def_args = []
#         def_keys = paras.args[-nb_def:]
#         def_dict = {k: v for k, v in zip(def_keys, def_args)}
#         for k in paras.args:
#             v = config_from_dicts(k, [kwargs] + json_dicts + [def_dict])
#             if v is not None:
#                 kwargs.update({k: v})
#         kwargs.update({'config_filenames': config_filenames})
#         kwargs.pop('config_filenames')
#         return func(*args, config_filenames=config_filenames, **kwargs)
#     return wrapper


# class Config:
#     """ Base class of configs """

#     def __init__(self,
#                  config_file=None,
#                  **kwargs):
#         self._configs = dict(**kwargs)
#         self._config_file = config_file

#     def load_config_file(self, file_name = None : str):
#         """ Load JSON config file, update config_file property if a new file_name is given. 
#         Inputs:
#             file_name: [Optional] JSON config file path.
#         Returns:
#             None
#         Raises:
#             //TODO: Complete
#         """
#         if file_name is None:
#             file_name = self._config_file
#         else:
#             self._config_file = file_name
#         with open(file_name, 'r') as fin:
#             self._configs = json.load(fin)

# """ Config utility class """
import json
import inspect
from functools import wraps
from pathlib import Path
from collections import ChainMap

from xlearn.utils.collections import AttrDict


def __parse_config_args(func, *args, config_files=None, **kwargs):
    """ Analysic func args and inputs/JSON file.

    Inputs:

        * args: tuple of positional arguments,                
        * config_files: filename or list of filenames of JSON file(s), *which may
          or may not present in original function's argument list*.
        * kwargs: dict of keyword arugments.

    Returns:
        1. a tuple, positional arguments,        
        2. a dict, keyword arugments.

    Raises:

    """
    # TODO: refine doc, add test.
    if isinstance(config_files, str):
        config_files = [config_files]
    if config_files is None:
        config_files = []
    json_dicts = []
    for fn in config_files:
        with open(fn, 'r') as fin:
            json_dicts.append(json.load(fin))
    sig = inspect.signature(func)
    kwargs['config_files'] = config_files
    kwargs = ChainMap(*([kwargs] + json_dicts))
    func_arg_keys = [k for k in sig.parameters]
    poped_keys = []
    func_arg_keys_tmp = list(func_arg_keys)
    for a, k in zip(args, func_arg_keys_tmp):
        poped_keys.append(func_arg_keys.pop(func_arg_keys.index(k)))
    kwargs_fine = {k: kwargs.get(k)
                   for k in func_arg_keys if kwargs.get(k) is not None}
    ba = sig.bind(*args, **kwargs_fine)
    ba.apply_defaults()
    return ba.args, ba.kwargs, poped_keys


def json_config(func):
    """ Add auto jason kwargs to function, by adding a preserved keyword 'config_files' """
    @wraps(func)
    def wrapper(*args, config_files=None, **kwargs):
        f_args, f_kwargs, _ = __parse_config_args(
            func, *args, config_files=config_files, **kwargs)
        return func(*f_args, **f_kwargs)
    return wrapper
