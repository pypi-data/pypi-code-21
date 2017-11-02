from .magicchain import MagicChain, MagicList
from pathlib import *
from copy import deepcopy
from .magicchain import MagicChain
from .utils import *
import glob


class MagicPath(MagicChain):

    def __init__(self, name, push_up=True):
        super().__init__(push_up=push_up)
        self.name = name
        self._parent_dir = ''

    @property
    def dir(self):
        """ The parent directory of this location"""
        return self.root._parent_dir

    @property
    def relpath(self):
        """ Relative path of this location """
        return Path(*self.ancestors(include_self=True).name)

    @property
    def path(self):
        """ Path of this location"""
        return Path(self.dir, *self.ancestors(include_self=True).name)

    @property
    def abspath(self):
        """ Absolute path of this location """
        return self.path.absolute()

    def set_dir(self, path):
        """ Set the parent directory """
        self.root._parent_dir = path
        return path

    def remove_parent(self):
        """ Remove parent from this path """
        new_parent = self.abspath.parent
        self._parent_dir = new_parent
        return super().remove_parent()

    def __repr__(self):
        return "<{}(\"{}\")>".format(self.__class__.__name__, self.name, self.relpath)

    def print(self, print_files=False, indent=4, max_level=None, level=0, list_missing=True):
        """
        Recursively print the file structure

        :param print_files: whether to print files
        :type print_files: boolean
        :param indent: number of spaces per indent
        :type indent: int
        :param max_level: max level depth to print
        :type max_level: int
        :param level: start at level
        :type level: int
        :param list_missing: whether to annotate files that do not exist
        :type list_missing: boolean
        :return: None
        :rtype: None
        """
        padding = '|   ' * level
        name = self.name
        if self.attr and name != self.attr:
            name += " (\"{}\")".format(self.attr)
        missing_tag = ''
        if list_missing and not self.exists():
            missing_tag = "*"
        print("{padding}{missing}{name}".format(missing=missing_tag, padding=padding, name=name))

        level += 1
        for name, child in self._children.items():
            child.print(print_files, indent, max_level, level, list_missing)

class MagicFile(MagicPath):

    def write(self, mode, data, *args, **kwargs):
        """ Write data to a file """
        return self.parent.write(self.name, mode, data, *args, **kwargs)

    def read(self, mode, *args, **kwargs):
        """ Read data from a file """
        return self.parent.read(self.name, mode, *args, **kwargs)

    def open(self, mode, *args, **kwargs):
        """ Opens a file for reading or writing """
        return self.parent.open(self.name, mode, *args, **kwargs)

    def exists(self):
        """ Whether the file exists """
        return Path(self.abspath).is_file()

    def rm(self):
        """ Removes file if it exists. """
        if self.exists():
            os.remove(str(self.abspath))


class MagicDir(MagicPath):

    @property
    def files(self):
        """
        Recursively returns all files <MagicFile> of this directory. Does not include parent directories.

        :return: list of MagicFiles
        :rtype: list
        """
        desc = self.descendents(include_self=True)
        return MagicList([d for d in desc if d.__class__ is MagicFile])

    @property
    def dirs(self):
        """
        Recursively returns all directories <MagicDir> of this directory. Does not include parent directories.

        :return: list of MagicDir
        :rtype: list
        """
        desc = self.descendents(include_self=True)
        return MagicList([d for d in desc if d.__class__ is self.__class__])

    @property
    def relpaths(self):
        """
        Returns all paths to all directories (includes parent_dir).

        :return: directory paths in this directory (inclusive)
        :rtype: list of PosixPath
        """
        return self.dirs.relpath

    @property
    def paths(self):
        """
        Returns all paths to all directories (includes parent_dir).

        :return: directory paths in this directory (inclusive)
        :rtype: list of PosixPath
        """
        return self.dirs.path

    @property
    def abspaths(self):
        """
        Returns all absolute paths to all directories (includes parent_dir).

        :return: directory absolute paths in this directory (inclusive)
        :rtype: list of PosixPath
        """
        return self.paths.absolute()

    def all_exists(self):
        """
        Whether all directories in the tree exist.

        :return: directory tree exists
        :rtype: boolean
        """
        return all(self.abspaths.is_dir())

    def mkdirs(self):
        """
         Creates all directories in the directory tree. Existing directories are ignored.

        :return: self
        :rtype: MagicDir
        """
        for p in self.abspaths:
            makedirs(p, exist_ok=True)
        return self

    def rmdirs(self):
        """
         Recursively removes all files and directories of this directory (inclusive)

        :return: self
        :rtype: MagicDir
        """
        if self.abspath.is_dir():
            rmtree(self.abspath)
        return self

    def cpdirs(self, new_parent):
        """
        Copies the directory tree to a new location. Returns the root of the newly copied tree.

        :param new_parent: path of new parent directory
        :type new_parent: basestring or PosixPath or Path object
        :return: copied directory
        :rtype: MagicDir
        """
        copytree(self.abspath, Path(new_parent, self.name))
        copied_dirs = deepcopy(self)
        copied_dirs.remove_parent()
        copied_dirs.set_dir(new_parent)
        return copied_dirs

    def mvdirs(self, new_parent):
        """ Moves the directory. If this directory has a parent connection, the connection will be broken and this
        directory will become a root directory. The original root will be left in place but will no longer have
        access to the moved directories. """
        oldpath = self.abspath
        self.remove_parent()
        copytree(oldpath, Path(new_parent, self.name))
        self.set_dir(new_parent)
        rmtree(oldpath)
        return self

    def exists(self):
        """ Whether the directory exists """
        return self.abspath.is_dir()

    def ls(self):
        """ Lists the files that exist in directory """
        return listdir(self.abspath)

    def glob(self, pattern):
        return glob.glob(str(Path(self.abspath, pattern)))

    # def collect(self):
    #     """ collects new directories that exist on the local machine and add to tree """

    def _get_if_exists(self, name, attr):
        if self.has(attr):
            c = self.get(attr)
            if c.name == name:
                return c

    # TODO: exist_ok kwarg
    def add(self, name, attr=None, push_up=True, make_attr=True):
        """
        Adds a new directory to the directory tree.

        :param name: name of the new directory
        :type name: basestring
        :param attr: attribute to use to access this directory. Defaults to name.
        :type attr: basestring
        :param push_up: whether to 'push' attribute to the root, where it can be accessed
        :type push_up: boolean
        :param make_attr: whether to sanitize attribute to access (e.g. '.secrets' and 'with' are not a valid
        attributes)
        :type make_attr:
        :return: new directory
        :rtype: MagicDir
        """
        if attr is None:
            attr = name
        e = self._get_if_exists(name, attr)
        if e and issubclass(e.__class__, MagicDir):
            return e
        if name in self.children.name:
            raise AttributeError("Dir name \"{}\" already exists for {}. Existing dirnames: {}".format(name, self,
                  ', '.join(self.children.name)))
        return self._create_and_add_child(attr, with_attributes={"name": name}, push_up=push_up, make_attr=make_attr)

    def add_file(self, name, attr=None, push_up=True, make_attr=True):
        """
        Adds a new file to the directory tree.

        :param name: name of the new file
        :type name: basestring
        :param attr: attribute to use to access this directory. Defaults to name.
        :type attr: basestring
        :param push_up: whether to 'push' attribute to the root, where it can be accessed
        :type push_up: boolean
        :param make_attr: whether to sanitize attribute to access (e.g. '.secrets' and 'with' are not a valid
        attributes)
        :type make_attr:
        :return: new directory
        :rtype: MagicDir
        """

        if attr is None:
            attr = name
        e = self._get_if_exists(name, attr)
        if e and issubclass(e.__class__, MagicFile):
            return e
        if name in self.files.name:
            raise AttributeError("File name \"{}\" already exists. Existing files: {}".format(name,
                  ', '.join(self.files.name)))
        file = MagicFile(name)
        file._parent = self
        self._add(attr, file, push_up=push_up, make_attr=make_attr)
        return file

    def write(self, filename, mode, data, *args, **kwargs):
        """ Write  a file at this location """
        makedirs(self.abspath)
        with self.open(str(Path(self.abspath, filename)), mode, *args, **kwargs) as f:
            print('writing data')
            print(data)
            f.write(data)

    def read(self, filename, mode, *args, **kwargs):
        """ Read a file at this location """
        with self.open(str(Path(self.abspath, filename)), mode, *args, **kwargs) as f:
            return f.read()

    def open(self, filename, mode, *args, **kwargs):
        """ Open a file at this location """
        makedirs(self.abspath)
        return fopen(str(Path(self.abspath, filename)), mode, *args, **kwargs)