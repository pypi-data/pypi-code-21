"""
"""
# Level-0:


# class FilesBatchWorker:
#     from .. import service, model

#     def __init__(self, fs=None, include_pattern=None, exclude_pattern=None, depth=1):
#         from fs.osfs import OSFS
#         fs = fs or OSFS('.')
#         self.fs = fs
#         self.filter = model.FilesFilter(
#             include_pattern, exclude_pattern, depth)

#     def ls(self):
#         """
#         List all files matches filters
#         """
#         self.service.Mapper.ls(self.fs, self.filter)

#     @classmethod
#     def merge(fs, filters, target=None, method=None):
#         """
#         Merge all files matches filters into one.
#         """
#         pass

#     @classmethod
#     def map(fs, filters, callback, args, kwargs):
#         """
#         Map callback to files like:
#             for f in valid_files:
#                 callback(*args, filename=f, **kwargs)
#         """
#         pass

#     @classmethod
#     def clear(fs, filters):
#         pass


# class DirsBatchWorker:
#     @classmethod
#     def ls(fs, filters, show_size=False):
#         """
#         List all files matches filters, show their properties.
#         """
#         pass

#     @classmethod
#     def merge(cls, fs, filters, target=None, is_check=True, is_auto_rename=True, rename_pattern=r'{name}.{id}.{suffix}'):
#         """
#         Merge directories, provide check, auto rename options.
#         """
#         pass

#     @classmethod
#     def clear(cls, fs, include_filters=None, exclude_filters=None, depth=1, dryrun=False):
#         from ..service import Mapper
#         from ..model import DirsFilter
#         from functools import partial
#         dirs = DirsFilter(include_filters=include_filters,
#                           exclude_filters=exclude_filters, depth=depth)
#         if dryrun:
#             print("The Following directories are going to be removed")
#             Mapper.map(fs, dirs, lambda d: print('[REMOVE]', d))
#         else:
#             Mapper.map(fs, dirs, fs.removetree)


# # Level-1
# def list_dirs(target, pattern):
#     pass


# def clear_dirs(target, include_filters, exclude_filters=None, depth=1, dryrun=False):
#     from dxpy.filesystem.smartfs import FS
#     with FS(target) as fs:
#         DirsBatchWorker.clear(fs, include_filters,
#                               exclude_filters, depth, dryrun)


from ..model.filters import DirectoriesFilter, FilesFilter
from ..service import Mapper
from ..exceptions import *
