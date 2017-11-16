""" File objects
"""
# TODO: Add yaml support

from abc import ABCMeta, abstractmethod
from dxpy.file_system.path import Path


class FileError(Exception):
    pass


class DxlFileExistsError(FileError, FileExistsError):
    pass


class FileNotFoundOrWrongTypeError(FileError, FileNotFoundError):
    def __init__(self, path, ftype):
        self.path = path
        self.ftype = ftype

    def __str__(self):
        msg = r"File {path} with type {ftype} not found."
        return msg.format(path=self.path, ftype=self.ftype)


# class Attrs:
#     @staticmethod
#     def get_attr_by_name(name):
#         for x in dir(Attrs):
#             x = getattr(Attrs, x)
#             if not type(x) == type(Attrs.FileAttrsABC):
#                 continue
#             if issubclass(x, Attrs.FileAttrsABC) and x.name == name:
#                 return x
#         raise NotValidAttrName(name)

#     @staticmethod
#     def get_attr_by_names(names):
#         return {Attrs.get_attr_by_name(n) for n in names}

#     @staticmethod
#     def get_attrs_by_path(path, file_system):
#         if isinstance(path, str):
#             path = Path(path)
#         if not FileSystem.exists(path):
#             raise FileNotFoundOrWrongTypeError(path.abs)
#         result = set()
#         for x in dir(Attrs):
#             x = getattr(Attrs, x)
#             if type(x) == type(Attrs.FileAttrsABC) and issubclass(x, Attrs.FileAttrsABC):
#                 result = result.union(x.test(path))
#         return result

#     class File(FileAttrsABC):
#         name = 'FILE'

#         @staticmethod
#         def test(path):
#             return {Attrs.File, } if FileSystem.is_file(path) else set()

#     class Dir(FileAttrsABC):
#         name = 'DIR'

#         @staticmethod
#         def test(path):
#             return {Attrs.Dir, } if FileSystem.is_dir(path) else set()

#     class Text(FileAttrsABC):
#         name = 'TEXT'

#         @staticmethod
#         def test(path):
#             return {Attrs.Text, } if path.suffix in {'.txt'} else set()

#     class Exec(FileAttrsABC):
#         name = 'EXEC'

#     class ShellScript(Exec):
#         name = 'SHELLSCRIPT'

#         @staticmethod
#         def test(path):
#             return {Attrs.ShellScript, } if path.suffix == '.sh' else set()

#     class WinExe(Exec):
#         name = 'WINEXE'

#         @staticmethod
#         def test(path):
#             return {Attrs.WinExe, } if path.suffix == '.exe' else set()

#     class Bin(FileAttrsABC):
#         name = 'BIN'

#     class NumpyData(Bin):
#         name = 'NUMPYDATA'

#         @staticmethod
#         def test(path):
#             return {Attrs.NumpyData, } if path.suffix in ['.npy', '.npz'] else set()

#     class NPY(NumpyData):
#         name = 'NPY'

#         @staticmethod
#         def test(path):
#             return {Attrs.NPY, } if path.suffix in ['.npy'] else set()

#     class NPZ(NumpyData):
#         name = 'NPZ'

#         @staticmethod
#         def test(path):
#             return {Attrs.NPZ, } if path.suffix in ['.npz'] else set()


# class FileAttrs:
#     def __init__(self, attrs=None):
#         if attrs is None:
#             self.attrs = set()
#             return
#         if isinstance(attrs, FileAttr):
#             self.attrs = attrs.attrs
#             return
#         if not isinstance(attrs, (list, tuple, set)):
#             attrs = {attrs}

#     def add(self, attr):
#         self.attrs.add(attr)

#     def __str__(self):
#         return '[' + ','.join(self.info) + ']'

#     @property
#     def brief(self):
#         return [x.name for x in self.attrs]

#     @property
#     def detail(self):
#         return self.brief

#     def hasattr(self, attr):
#         return any(issubclass(x, attr) for x in self.attrs)

#     @property
#     def is_exe(self):
#         return self.hasattr(Attrs.Exec)

#     @property
#     def is_dir(self):
#         return self.hasattr(Attrs.Dir)

#     def check(self, path, file_system):
#         for aAttr in self.attrs:
#             if not aAttr.test(path, file_system):
#                 raise FileAttrError(path, self.attrs, aAttr)
#         return None


class FileAbstract(metaclass=ABCMeta):
    """ File class focus on existance.
    """

    def __init__(self, path, file_system):
        self.path = Path(path)
        self.fs = file_system
        if not self.check(self.path, self.fs):
            raise FileNotFoundOrWrongTypeError(self.path, self.ftype)

    @staticmethod
    def check(path, file_system):
        if isinstance(path, str):
            path = Path(path)
        return file_system.exists(path)

    def copy_to(self, path):
        result = self.fs.copy(path, self.path)
        return result

    def move_to(self, path):
        result = self.fs.move(path, self.path)
        return result

    @abstractmethod
    def update(self, content):
        return NotImplementedError

    @abstractmethod
    def delete(self):
        raise NotImplementedError

    @property
    def ftype(self):
        return {'FileAbstract'}

    @property
    def brief(self):
        """ A JSON serilizable info dict.
        """
        types = [str(x) for x in self.ftype]
        types.sort()
        return {
            'path': self.path.abs,
            'name': self.path.name,
            'type': types}

    @property
    def detail(self):
        result = self.brief
        result.update({
            'parent': self.path.parent,
            'parts': self.path.parts(),
        })
        return result


class Directory(FileAbstract):
    def __init__(self, path, file_system, factory=None):
        if factory is None:
            factory = FileFactory
        FileAbstract.__init__(self, path, file_system)
        self.factory = factory
        if not self.check(self.path, self.fs):
            raise FileNotFoundOrWrongTypeError(self.path, self.ftype)

    @staticmethod
    def check(path, file_system):
        if isinstance(path, str):
            path = Path(path)
        return file_system.Directory.check(path)

    def delete(self):
        self.fs.Directory.delete(self.path)
        return None

    def update(self):
        return self

    @property
    def ftype(self):
        result = super().ftype
        result.add('Directory')
        return result

    @property
    def detail(self):
        children_path = self.fs.Directory.glob(self.path)
        children_brief = [FileFactory.get_file(
            cp, self.fs) for cp in children_path]

        result = super().detail
        result.update({
            "children": children_brief
        })
        return result


class NormalFile(FileAbstract):
    def __init__(self, path, file_system):
        FileAbstract.__init__(path, file_system)
        if not self.check(self.path, self.fs):
            raise FileNotFoundOrWrongTypeError(self.path, self.ftype)

    @staticmethod
    def check(path, file_system):
        return file_system.File.check(path)

    def delete(self):
        self.fs.File.delete(self.path)

    def update(self):
        return self

    @property
    def ftype(self):
        result = super().ftype
        result.add('NormalFile')
        return result


class Exec(NormalFile):
    pass


class FileFactory:
    @staticmethod
    def get_file(path, file_system):
        fa = FileAttr().set_attrs(path)
        if fa.hasattr(Attrs.Dir):
            return Directory(path)
        if fa.hasattr(Attrs.File):
            return NormalFile(path)

    @staticmethod
    def create_file(path, file_system, cls):
        pass
