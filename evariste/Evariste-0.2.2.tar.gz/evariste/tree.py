# Copyright Louis Paternault 2016
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

"""Directory representation and compilation."""

import configparser
import functools
import logging
import os
import pathlib
import queue
import tarfile

from evariste import plugins, utils, errors, multithread
from evariste.plugins.action import DirectoryAction
from evariste.hooks import set_methodhook

LOGGER = logging.getLogger(__name__)

def get_tree_plugins(self, *args, **kwargs):
    """Given the argument of :meth:`Tree.__init__`, return a :class:`AllPlugins` instance."""
    # pylint: disable=unused-argument
    if isinstance(self, Root):
        root = self
    else:
        root = kwargs['parent']
        while root.parent is not None:
            root = root.parent
    return root.shared.builder.plugins

@functools.total_ordering
class Tree:
    """Directory tree"""
    # pylint: disable=too-many-instance-attributes

    @set_methodhook("buildtreeitem", getter=get_tree_plugins)
    def __init__(self, path, *, parent):
        self._subpath = {}
        self.report = None
        self.ignored = []
        self.parent = parent
        self.config = None
        if parent is not None:
            self.basename = pathlib.Path(path)
            self.from_fs = parent.from_fs / self.basename
            self.from_source = parent.from_source / self.basename
            self.vcs = self.parent.vcs
            self.shared = self.parent.shared
        self.local = self.shared.get_tree_view(path)
        self._set_ignore()
        self._set_config()

    def __hash__(self):
        return hash((hash(self.parent), self.from_fs))

    @property
    def relativename(self):
        """Return a 'relative' path.

        * For root, return path relative to file system (or directory of setup file).
        * For non-root, return path relative to parent (i.e. basename of path).
        """
        if isinstance(self, Root):
            return self.from_fs
        else:
            return self.basename

    @staticmethod
    def is_root():
        """Return ``True`` iff ``self`` is the root."""
        return False

    @property
    def depth(self):
        """Return the depth of the path.

        The root has depth 0, and depth of each path is one more than the depth
        of its parent.
        """
        if isinstance(self, Root):
            return 0
        else:
            return 1 + self.parent.depth

    @property
    def root(self):
        """Return the root of the tree."""
        if self.is_root():
            return self
        return self.parent.root

    def find(self, path):
        """Return ``True`` iff ``path`` exists, as a subpath of ``self``.

        Argument can be:
        - a string (:type:`str`);
        - a :type:`pathlib.Path` object;
        - a tuple of strings, as a list of directories and (optional) final file.
        """
        if isinstance(path, str):
            pathtuple = pathlib.Path(path)
        elif isinstance(path, pathlib.Path):
            pathtuple = path.parts
        else:
            pathtuple = path

        if not pathtuple:
            return True
        if pathtuple[0] in self:
            return self[pathtuple[0]].find(pathtuple[1:])
        return False

    def add_subpath(self, sub):
        """Add a subpath"""
        if len(sub.parts) > 1:
            self[sub.parts[0]].add_subpath(pathlib.Path(*sub.parts[1:]))
        else:
            self[sub.parts[0]] # pylint: disable=pointless-statement

    def __iter__(self):
        return iter(self._subpath)

    def keys(self):
        """Iterator over subpaths (as :class:`str` objects)."""
        yield from self._subpath.keys()

    def values(self):
        """Iterator over subpaths (as :class:`Tree` objects)."""
        yield from self._subpath.values()

    def __contains__(self, key):
        return key in self._subpath

    def __getitem__(self, key):
        if key not in self:
            if (self.from_fs / key).is_dir():
                path_type = Directory
            else:
                path_type = File
            self._subpath[key] = path_type(key, parent=self)
        return self._subpath[key]

    def __delitem__(self, item):
        pathitem = pathlib.Path(item)
        if len(pathitem.parts) != 1:
            raise errors.EvaristeBug(
                "Argument '{}' should be a single directory or file, "
                "not a 'directory/directory' or directory/file'."
                )
        if str(pathitem) in self:
            del self._subpath[str(pathitem)]
            if (not self._subpath) and self.is_dir() and self.parent is not None:
                del self.parent[self.basename]


    def __str__(self):
        return self.from_fs.as_posix()

    def __len__(self):
        return len(self._subpath)

    def __eq__(self, other):
        return self.from_source == other.from_source

    def __lt__(self, other):
        if isinstance(self, Directory) and not isinstance(other, Directory):
            return True
        if not isinstance(self, Directory) and isinstance(other, Directory):
            return False
        return self.from_source < other.from_source

    def is_dir(self):
        """Return `True` iff `self` is a directory."""
        return issubclass(self.__class__, Directory)

    def is_file(self):
        """Return `True` iff `self` is a file."""
        return issubclass(self.__class__, File)

    def walk(self, dirs=False, files=True):
        """Iterator over files or directories  of `self`.

        :param bool dirs: If `False`, do not yield directories.
        :param bool files: If `False`, do not yield files.
        """
        if (
                (dirs and self.is_dir())
                or
                (files and self.is_file())
            ):
            yield self
        for sub in sorted(self):
            yield from self[sub].walk(dirs, files)

    def iter_ignored(self):
        """Iterate over ignored paths."""
        # Recursive call
        for sub in self:
            yield from self[sub].iter_ignored()

        # Process ``self``
        for regexp in self.ignored:
            for file in self.from_fs.glob(str(regexp)):
                yield file.relative_to(self.root.from_fs)

        # Process ``self``
        for file in self.config_files(parent=False):
            yield pathlib.Path(file).relative_to(self.root.from_fs)

    def prune(self, path):
        """Remove a file.

        Argument can be either a :class:`pathlib.Path` or a :class:`tuple`.
        """
        if isinstance(path, tuple):
            parts = path
        elif isinstance(path, pathlib.Path):
            parts = path.parts
        else:
            raise ValueError
        if len(parts) == 1:
            del self[parts[0]]
        else:
            self[parts[0]].prune(parts[1:])

    def _parent_config_files(self):
        """Iterate over the names of configuration files affecting parents of ``self``.
        """
        if self.parent is not None:
            yield from self.parent.config_files(parent=True)

    def _set_ignore(self):
        """Set the list of ignored regular expressions."""
        raise NotImplementedError()

    def _set_config(self):
        """Set the configuration of file or directory."""
        # Set configuration of `self`
        config = configparser.ConfigParser(allow_no_value=True)
        for filename in self.config_files(parent=True):
            with open(filename) as file:
                config.read_file(file)
        self.config = utils.DeepDict.from_configparser(config)


    def config_files(self, parent=False):
        """Iterator over the list of configuration files."""
        raise NotImplementedError()

    def iter_depends(self):
        """Iterate files that are dependencies of others."""
        raise NotImplementedError()

    def format(self, string):
        """Format given string, with several variables related to ``self``.
        """
        suffix = self.from_source.suffix
        if suffix.startswith("."):
            suffix = suffix[1:]
        return string.format(
            dirname=self.parent.from_fs.as_posix(),
            filename=self.basename,
            fullname=self.from_fs.as_posix(),
            extension=suffix,
            basename=self.basename.stem,
            )


    def render_readme(self, renderers, *args, **kwargs):
        """Find and render the readme corresponding to ``self``.

        If no readme was found, return ``None``.
        """
        for renderer in renderers:
            for filename in renderer.iter_readme(
                    self.from_fs,
                    directory=self.is_dir(),
                ):
                return renderer.render(filename, *args, **kwargs)
        return None

    def iter_readmes(self, renderers):
        """Iterate over readme files."""
        for renderer in renderers:
            for filename in renderer.iter_readme(
                    self.from_fs,
                    directory=self.is_dir(),
                ):
                yield pathlib.Path(filename).relative_to(self.root.from_fs)
                return

    def full_depends(self):
        """Return the list of all dependencies of this tree (recursively for directories)."""
        raise NotImplementedError()


class Directory(Tree):
    """Directory"""

    def _set_ignore(self):
        """Set the list of ignored regular expressions."""
        ignorename = os.path.join(self.from_fs.as_posix(), ".evsignore")
        if os.path.exists(ignorename):
            self.ignored.append(os.path.basename(ignorename))
            with open(ignorename) as file:
                for line in file.readlines():
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("#"):
                        continue
                    try:
                        # Fake glob, to catch lines with invalid syntax.
                        for _ in self.from_fs.glob(line):
                            break
                    except ValueError as error:
                        LOGGER.warning("Line '{}' has been ignored in file '{}': {}.".format(
                            line,
                            ignorename,
                            str(error),
                            ))
                        continue
                    self.ignored.append(line)

    def config_files(self, parent=False):
        """Iterator over the names of configuration files specific to ``self``
        """
        if parent:
            yield from self._parent_config_files()

        name = os.path.join(self.from_fs.as_posix(), ".evsconfig")
        if os.path.exists(name):
            yield name

    def feed_compile_tasks(self, *, taskqueue, to_prune, to_report):
        """Put tasks corresponding to actions to perform on files, in the queue.

        :param multithread.Queue taskqueue: Queue of tasks to perform in
            parallel, now.
        :param multithread.Queue to_prune: Queue of tasks to perform when
            every task of ``taskqueue`` has been executed, to prune files that
            are to be ignored.
        :param multithread.Queue to_report: Queue of tasks to perform when
            every task of ``taskqueue`` has been executed, to build the
            :attr:`Tree.report` object.
        """
        priority = 0
        for sub in sorted(self):
            if self[sub].is_file():
                taskqueue.put(
                    functools.partial(self[sub].compile, to_prune=to_prune)
                    )
            else:
                priority = max(
                    priority,
                    self[sub].feed_compile_tasks(
                        taskqueue=taskqueue,
                        to_prune=to_prune,
                        to_report=to_report,
                        )
                    )

        to_report.put(multithread.Task(
            (1, priority+1),
            self._set_report,
            ))

        return priority + 1

    def _set_report(self):
        """Build and set `self.report`."""
        self.report = DirectoryAction(self.shared).compile(self)

    def iter_depends(self):
        """Iterate files that are dependencies of others."""
        # We cannot use `for sub in self:` here because dictionnary
        # `self._subpath` may change during iteration.
        for sub in list(self):
            if sub in self:
                yield from self[sub].iter_depends()

    def iter_readmes(self, renderers):
        renderers = list(renderers)
        yield from super().iter_readmes(renderers)

        for sub in self:
            yield from self[sub].iter_readmes(renderers)

    def full_depends(self):
        for sub in self:
            yield from self[sub].full_depends()


class File(Tree):
    """File"""

    def _set_ignore(self):
        """Set the list of ignored regular expressions."""
        for name in ["{}.ignore", ".{}.ignore"]:
            if os.path.exists(os.path.join(
                    self.parent.from_fs.as_posix(),
                    name.format(self.basename),
                )):
                self.parent.ignored.append(self.basename)
                self.parent.ignored.append(name.format(self.basename))

    def config_files(self, parent=False):
        if parent:
            yield from self._parent_config_files()

        for name in [".{}.evsconfig", "{}.evsconfig"]:
            name = os.path.join(
                self.parent.from_fs.as_posix(),
                name.format(self.basename),
                )
            if os.path.exists(name):
                yield name

    def compile(self, *, to_prune):
        """Compile file."""
        with self.shared.builder.lock.thread_unsafe():
            LOGGER.info("Compiling '{}'…".format(self.from_source))
            try:
                if not self.shared.builder.plugins.get_plugin('changed').compile(self):
                    # Nothing has changed: it is useless to compile this again.
                    compiler = self.shared.builder.plugins.get_plugin('action.useless')
                elif self.config['action']['plugin'] is not None:
                    compiler = self.shared.builder.plugins.get_plugin('{}.{}'.format(
                        'action',
                        self.config['action']['plugin'],
                        ))
                else:
                    compiler = self.shared.builder.plugins.match_plugin('action', self.from_fs)
            except plugins.NoMatch:
                to_prune.put(multithread.Task(
                    (0, -self.depth),
                    functools.partial(
                        self.parent.__delitem__,
                        self.basename,
                    )
                    ))
                LOGGER.info("Compiling '{}': ignored.".format(self.from_source))
                return

            with self.shared.builder.plugins.apply_context_hook("compilefile", args=[self]):
                self.report = compiler.compile(self)
            if self.report.success:
                LOGGER.info("Compiling '{}': success.".format(self.from_source))
            else:
                LOGGER.info("Compiling '{}': failed.".format(self.from_source))

    def iter_depends(self):
        """Iterate over dependencies."""
        if self.report.success:
            for path in self.report.depends:
                yield path.resolve().relative_to(
                    self.root.from_fs.resolve()
                    )

    @set_methodhook("makearchive")
    @functools.lru_cache(maxsize=None)
    def make_archive(self, destdir):
        """Make an archive of ``self`` and its dependency.

        Stes are:
        - build the archive;
        - copy it to ``destdir``;
        - return the path of the archive, relative to ``destdir``.

        If ``self`` has no dependencies, consider the file as an archive.

        It can be called several times: the archive will be built only once.
        """

        def common_root(files):
            """Look for the common root of files given in argument.

            Returns a tuple of `(root, relative_files)`, where
            `relative_files` is a list of `files`, relative to the root.
            """
            files = [
                file.resolve()
                for file
                in files
                if file.resolve().as_posix().startswith(self.root.from_fs.resolve().as_posix())
                ]
            root = pathlib.Path()
            while True:
                prefixes = [path.parts[0] for path in files]
                if len(set(prefixes)) != 1:
                    break
                prefix = prefixes[0]
                files = [
                    file.relative_to(prefix)
                    for file
                    in files
                    ]
                root /= prefix
            return root.relative_to(self.root.from_fs.resolve()), files

        if (
                # Compilation was successful
                self.report.success
                # File has not been compiled again
                and not self.shared.builder.plugins.get_plugin('changed').compile(self)
                # Archive has already been generated
                and 'archivepath' in self.shared.tree[self.from_source]['changed']
            ):
            return self.shared.tree[self.from_source]['changed']['archivepath']

        if len(self.report.full_depends) == 1:
            utils.copy(self.from_fs.as_posix(), (destdir / self.from_source).as_posix())
            return self.from_source
        else:
            archivepath = self.from_source.with_suffix(
                "{}.{}".format(self.from_source.suffix, 'tar.gz')
                )
            os.makedirs(os.path.dirname((destdir / archivepath).as_posix()), exist_ok=True)

            archive_root, full_depends = common_root(self.report.full_depends)
            with tarfile.open(
                (destdir / archivepath).as_posix(),
                mode='w:gz',
                ) as archive:
                for file in full_depends:
                    archive.add(
                        (self.root.from_fs / archive_root / file).as_posix(),
                        file.as_posix(),
                        )
            return archivepath

    def last_modified(self):
        """Return the last modified date and time of ``self``."""
        return self.vcs.last_modified(self.from_fs)

    def full_depends(self):
        yield from self.report.full_depends

    def depends(self):
        """Iterator over dependencies of this file (but not the file itself)."""
        yield from self.report.depends

class Root(Directory):
    """Root object (directory with no parents)"""

    def __init__(self, path, *, vcs=None, shared=None):
        self.vcs = vcs
        self.shared = shared
        self.from_fs = path
        self.from_source = pathlib.Path(".")
        self.basename = pathlib.Path(".")
        super().__init__(path, parent=None)

    @staticmethod
    def is_root():
        return True

    def root_compile(self):
        """Recursively compile files.."""
        self.prune_ignored()
        workers = self.shared.setup["arguments"]["jobs"]
        with multithread.Pool(workers) as pool:
            to_prune = queue.PriorityQueue()
            to_report = queue.PriorityQueue()
            self.feed_compile_tasks(
                taskqueue=pool.queue,
                to_prune=to_prune,
                to_report=to_report
                )
        while not to_prune.empty():
            to_prune.get().run()
        self.prune_depends()
        while not to_report.empty():
            to_report.get().run()

    def prune_ignored(self):
        """Prune ignored files."""
        for file in list(self.iter_ignored()):
            if self.find(file):
                self.prune(file)

    def prune_depends(self):
        """Prune dependencies."""
        for file in list(self.iter_depends()):
            if self.find(file):
                self.prune(file)

    @classmethod
    def from_vcs(cls, repository):
        """Return a directory, fully set."""
        tree = cls(repository.source, vcs=repository, shared=repository.shared)
        for path in repository.walk():
            tree.add_subpath(pathlib.Path(path))
        return tree
