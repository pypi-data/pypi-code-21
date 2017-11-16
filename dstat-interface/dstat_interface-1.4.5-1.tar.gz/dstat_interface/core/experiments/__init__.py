# __all__ = []
#
# import pkgutil
# import inspect
# from . import cal, chronoamp, cv
#
#
# for loader, name, is_pkg in pkgutil.walk_packages(__path__):
#     print loader, name, is_pkg
#     module = loader.find_module(name).load_module(name)
#
#     for name, value in inspect.getmembers(module):
#         if name.startswith('__'):
#             continue
#
#         globals()[name] = value
#         __all__.append(name)