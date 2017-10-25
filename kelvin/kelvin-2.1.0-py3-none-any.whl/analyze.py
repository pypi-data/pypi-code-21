
import os, sys, logging, re
import modulefinder
from modulefinder import ReplacePackage
from os.path import join, exists, dirname, abspath, splitext
from collections import namedtuple

from .utils import split

DEFAULT_EXCLUDES = split("""
    _dummy_thread _dummy_threading _emx_link _gestalt _posixsubprocess ce doctest fcntl grp
    java.lang org.python.core os2 os2emxpath posix pwd pydoc readline riscos
    riscosenviron riscospath rourl2path sitecustomize termios unittest usercustomize vms_lib
    win32api win32con win32pipe

    _frozen_importlib _frozen_importlib_external

    # IIRC, OS-specific modules are loaded as os.path, so there isn't an actual file os/path.
    os.path

    # Module finder believes the following are modules and cannot import them so they are excluded by default.

    ctypes._SimpleCData
    xml.dom.EMPTY_NAMESPACE xml.dom.EMPTY_PREFIX xml.dom.Node xml.dom.XMLNS_NAMESPACE xml.dom.XML_NAMESPACE
    """)


Analysis = namedtuple('Analysis', 'modules extensions missing')


class Analyzer:
    """
    Analyzes the source to collect all of the dependencies.
    """
    def __init__(self, include=None, exclude=None, path=None, report=None, logger=None,
                 package_paths=None, expand=None, *, script):
        """
        expand
          A list of package names for which *all* files in the package should be included, not
          just those that module finder has determined are used.

          The special name '.' can be used to represent the directory the main script is in.
        """
        self.script  = script
        self.path    = path
        self.include = include
        self.exclude = DEFAULT_EXCLUDES
        self.report  = report
        self.logger  = logger or logging.getLogger('analyze')

        self.package_paths = package_paths
        self.expand = expand

        if exclude:
            self.exclude += exclude

    def get_finder(self):
        """
        Returns a ModuleFinder instance configured for this application.
        """
        path = self.path or []
        path += sys.path

        if self.package_paths:
            for pkg, dirs in self.package_paths.items():
                for dir in dirs:
                    modulefinder.AddPackagePath(pkg, dir)

        ReplacePackage('_xmlplus', 'xml')

        finder = modulefinder.ModuleFinder(
            path=path,
            excludes=self.exclude,
            debug=bool(self.report)
        )
        return finder

    def analyze(self):
        finder = self.get_finder()
        finder.run_script(self.script)

        if self.include:
            for module in self.include:
                finder.import_hook(module)

        # Add __kelvin__, our startup module.

        fqn = join(dirname(abspath(__file__)), '__kelvin__.py')
        assert exists(fqn), 'Not found: %r' % fqn
        finder.load_file(fqn)

        self.find_submodules(finder, 'encodings')

        if self.report:
            finder.report()

        return self.parse_mf_results(finder)

    def parse_mf_results(self, finder):
        modules    = []
        extensions = []

        for item in finder.modules.values():
            src = item.__file__
            if not src:
                # Part of Python
                continue

            ext = splitext(src)[1]

            if ext in ['.py', '.pyc', '.pyo']:
                modules.append(item)
                continue

            if ext == '.pyd':
                extensions.append(item)
                continue

            raise Exception('Do not know how to handle {!r}'.format(src))

        missing, _maybe_ = finder.any_missing_maybe()

        if self.expand:
            # If the user has specified a package in `expand`, it is probably because a lot of
            # stuff is dynamically imported.  Since we are including all code in the package,
            # there is not anything really missing.
            regexp = re.compile(r'^(%s)\.' % ('|'.join(re.escape(name) for name in self.expand)))
            missing = [name for name in missing if not regexp.match(name)]

        # It looks to me like anything in bad_modules with a caller '-' is bogus.  When
        # building an app with asyncio, asyncio.DefaultEventLoopPolicy is shown as a *module*.
        # It should be an object.  Others like multiprocessing.get_context look like functions.

        for name, callers in finder.badmodules.items():
            if len(callers) == 1 and '-' in callers:
                self.logger.debug('Ignoring "bad module" %r name due to unspecified caller', name)
                try:
                    missing.remove(name)
                except ValueError:
                    # The module is not in `modules`.  It could have been in the exclude list.
                    # For some reason these still end up in the badmodules list.
                    pass

        # I don't know why (yet), but finder puts things into badmodules even though they are
        # supposed to be excluded.  We'll manually remove them until we get to the bottom of
        # this.
        missing = set(missing) - set(self.exclude)

        return Analysis(modules, extensions, missing)

    def find_submodules(self, finder, name):
        self.logger.debug('Importing all submodules for %s', name)
        finder.import_hook(name)
        module = finder.modules[name]
        for submodule in finder.find_all_submodules(module):
            finder.import_hook(name + '.' + submodule)
