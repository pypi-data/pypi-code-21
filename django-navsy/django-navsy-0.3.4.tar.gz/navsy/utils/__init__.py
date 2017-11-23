# -*- coding: utf-8 -*-

from django.utils.module_loading import import_string


def import_function(path):
    try:
        func = import_string(path)
        if hasattr(func, '__call__'):
            return func
        else:
            return None
    except ImportError:
        return None


# from importlib import import_module


# def import_function(path):

#     if not path:
#         return None

#     func_path = path
#     mod_name, func_name = func_path.rsplit('.', 1)

#     if mod_name and func_name:

#         try:
#             mod = import_module(mod_name)

#             try:
#                 func = getattr(mod, func_name)

#                 if hasattr(func, '__call__'):
#                     return func
#                 else:
#                     return None

#             except AttributeError:
#                 return None

#         except ImportError:
#             return None

#     return None
