# Copyright Louis Paternault 2015
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""A rag-bag of utility functions that did not fit anywhere else."""

from collections import defaultdict
import contextlib
import functools
import io
import os
import pkgutil
import re
import shutil
import sys

RE_BRACKETS = re.compile('{[^{]*}')

def copy(source, destination):
    """Copy ``source`` to ``destination``, creating directories if necessary."""
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    shutil.copy2(source, destination)

def copytree(source, destination):
    """Recursively copy a tree.

    Note: We do not use :func:`shutil.copytree` because it raises an error if
    destination already exists, which we do not want.
    """
    os.makedirs(source, exist_ok=True)
    for path in os.listdir(source):
        sourceitem = os.path.join(source, path)
        destitem = os.path.join(destination, path)
        if os.path.isdir(sourceitem):
            copytree(sourceitem, destitem)
        else:
            copy(sourceitem, destitem)

def partial_format(string, *args, **kwargs):
    """Format string, leaving unfilled fields untouched.

    >>> partial_format("To {verb} or {negation} to {verb}", negation="not")
    'To {verb} or not to {verb}'
    """
    dictionary = {
        field[1:-1]: field
        for field
        in re.findall(RE_BRACKETS, string)
        }

    dictionary.update(kwargs)
    return string.format(*args, **dictionary)

@contextlib.contextmanager
def smart_open(filename, mode="w", encoding="utf8"):
    """Open filename, standard output, or nothing.

    If ``filename`` is:

    * ``""`` (the empty string): return a fake file object, which is empty if
      file is open for reading, can be written in if file is open for writing;
    * ``"-"`` (a dash): read from standard input, or write to standard output
      (depending on mode);
    * any other: open the given file.
    """
    if (not filename) or (not filename.strip()):
        with io.StringIO() as file:
            yield file
    elif filename.strip() == "-":
        if 'w' in mode:
            yield sys.stdout
        elif 'r' in mode:
            yield sys.stdin
    else:
        with open(filename, mode, encoding=encoding) as file:
            yield file


def yesno(arg):
    """Interpret some variable as a boolean.

    >>> yesno("y")
    True
    >>> yesno("0")
    False
    >>> yesno("1")
    True
    >>> yesno("Yes")
    True
    >>> yesno("True")
    True
    >>> yesno("something senseless")
    False
    >>> yesno(None)
    False
    """
    if isinstance(arg, bool):
        return arg
    try:
        return bool(int(arg))
    except (ValueError, TypeError):
        pass
    if isinstance(arg, str):
        return (arg.lower() in ['y', 'yes', 'true'])
    return bool(arg)

class ChangeDir:
    """Context manager to change and restore current directory."""
    # pylint: disable=too-few-public-methods

    def __init__(self, directory):
        if not directory:
            directory = "."
        self._newdir = directory
        self._olddir = os.getcwd()

    def __enter__(self):
        self._olddir = os.getcwd()
        os.chdir(self._newdir)

    def __exit__(self, *args, **kwargs):
        os.chdir(self._olddir)

def expand_path(path):
    """Return ``path`` where environment variables and user directory have been expanded."""
    return os.path.expanduser(os.path.expandvars(path))

class DeepDict(defaultdict):
    """Dictionary of dictionary of ... of dictionaries."""

    def __init__(self, depth, dictionary=None):
        if dictionary is None:
            dictionary = {}

        self.depth = depth
        if depth == 1:
            factory = lambda: None
        else:
            factory = functools.partial(self.__class__, depth-1)

        super().__init__(factory)
        for key, value in dictionary.items():
            self[key].update(value)

    @classmethod
    def from_configparser(cls, config):
        """Create a :class:`DeepDict` object from a :class:`configparser.ConfigParser` object."""
        dictionary = cls(2)
        for section in config.sections():
            for option in config.options(section):
                dictionary[section][option] = config.get(section, option)
        return dictionary

    def get_subkey(self, subkey):
        """Return the first `self[ANY][subkey]`, when `ANY` is any dictionary key."""
        for key in self:
            if subkey in self[key]:
                return self[key][subkey]
        raise KeyError(subkey)

    @property
    def __dict__(self):
        """Convert self to regular :type:`dict`."""
        if self.depth == 1:
            return dict(self)
        else:
            return {
                key: vars(value)
                for (key, value)
                in self.items()
                }

def iter_modules(path, prefix, logger=None):
    """Iterate over modules.

    :arg list path: List of paths to look for modules in.
    :arg str prefix: String to output on the front of every module name on
        output.
    :arg function logger: Function used to print logging error. May be `None`
        to discard logging.
    """
    for module_finder, name, __is_pkg in pkgutil.walk_packages(path, prefix):
        if name in sys.modules:
            module = sys.modules[name]
        else:
            try:
                module = module_finder.find_spec(name).loader.load_module()
            except ImportError as error:
                if logger is not None:
                    logger("[plugins] Could not load module {}: {}".format(name, str(error)))
                continue
        yield module
