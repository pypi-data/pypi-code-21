from .magicchain import MagicChain
from pathlib import *
import os
import shutil
from copy import deepcopy
import glob
from .utils import *

class MagicDir(MagicChain):

    def __init__(self, name, push_up=True, parent=None):
        super().__init__(parent=parent, push_up=push_up)
        self.name = name
        self._parent_dir = ''

    @property
    def dir(self):
        return self.root._parent_dir

    def set_dir(self, path):
        self.root._parent_dir = path
        return path

    # @dir.setter
    # def dir(self, path):
    #     self.set_dir(path)

    def mkdirs(self):
        for p in self.abspaths:
            makedirs(p, exist_ok=True)
        return self

    def rmdirs(self):
        if self.abspath.is_dir():
            rmtree(self.abspath)
        return self

    def cpdirs(self, new_parent):
        copytree(self.abspath, Path(new_parent, self.name))
        copied_dirs = deepcopy(self)
        copied_dirs.delete()
        copied_dirs.set_dir(new_parent)
        return copied_dirs

    def mvdirs(self, new_parent):
        oldpath = self.abspath
        self.delete()
        copytree(oldpath, Path(new_parent, self.name))
        self.set_dir(new_parent)
        rmtree(oldpath)

    def delete(self):
        new_parent = self.abspath.parent
        self._parent_dir = new_parent
        return super().delete()

    def ls(self):
        return listdir(self.abspath)

    def glob(self, pattern):
        return glob.glob(str(Path(self.abspath, pattern)))

    def collect(self):
        """ collects new directories that exist on the local machine and add to tree """

    def open(self, filename, mode, *args, **kwargs):
        return fopen(str(Path(self.abspath, filename)), mode, *args, **kwargs)

    def write(self, filename, mode, data, *args, **kwargs):
        with self.open(filename, mode, *args, **kwargs) as f:
            f.write(data)

    def read(self, filename, mode, *args, **kwargs):
        with self.open(filename, mode, *args, **kwargs) as f:
            return f.read()

    def all_exists(self):
        return all(self.abspaths.is_dir())

    def exists(self):
        return self.abspath.is_dir()

    def add(self, name, alias=None):
        if alias is None:
            alias = name
        if name in self.children.name:
            raise AttributeError("Folder name \"{}\" already exists. Existing folders: {}".format(name, ', '
                                                                                                        ''.join(
                    self.childen.name)))
        return super()._create_child(alias, with_attributes={"name": name})

    # @property
    # def list(self):
    #     return self.children.abspath

    @property
    def path(self):
        return Path(self.dir, *self.ancestors(include_self=True).name)

    @property
    def abspath(self):
        return self.path.absolute()

    @property
    def paths(self):
        return self.descendents(include_self=True).path

    @property
    def abspaths(self):
        return self.paths.absolute()

    def print(self, print_files=False, indent=4, max_level=None, level=0, list_missing=True):
        padding = '|   ' * level
        name = self.name
        if self.alias and name != self.alias:
            name += " (\"{}\")".format(self.alias)
        missing_tag = ''
        if list_missing and not self.exists():
            missing_tag = "*"
        print("{padding}{missing}{name}".format(missing=missing_tag, padding=padding, name=name))

        level += 1
        for name, child in self._children.items():
            child.print(print_files, indent, max_level, level, list_missing)