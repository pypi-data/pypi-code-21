import sys, os, shutil
from os.path import isdir, join, splitext, basename
import logging

class Builder:
    """
    Builds the executable and copies files to the distribution directory.
    """
    def __init__(self, include=None, exclude=None, path=None, report=None, logger=None,
                 package_paths=None, subsystem='console', filename=None, expand=None,
                 extra=None, version_strings=None,
                 *, script, dist, version):
        """
        See the README.rst file for a description of the parameters.
        """
        if subsystem not in ('console', 'windows'):
            raise ValueError('subsystem must be "windows" or "console"')

        self.script  = script
        self.path    = path
        self.include = include
        self.exclude = exclude
        self.report  = report
        self.package_paths = package_paths
        self.logger = logger or logging.getLogger('kelvin')
        self.subsystem = subsystem
        self.expand = expand

        if filename:
            if os.path in filename:
                raise ValueError("filename must not contain a path")
        else:
            filename = splitext(basename(script))[0] + '.exe'
        self.filename = filename

        self.dist = dist
        self.extra = extra
        self.version = version
        self.version_strings = version_strings

    def build(self):
        """
        Build the distribution into the dist directory.

        This will create the dist directory if necessary or delete the contents if it already
        exists.
        """
        self.logger.info('Building to %s', self.dist)
        self.prepare_dist_dir()

        from .analyze import Analyzer
        from .dlls import DllFinder

        analyzer = Analyzer(script=self.script, report=self.report, path=self.path, package_paths=self.package_paths,
                            include=self.include, exclude=self.exclude, expand=self.expand)
        analysis = analyzer.analyze()

        if analysis.missing:
            print('Missing')
            for name in sorted(analysis.missing):
                print('-', name)
            sys.exit(1)

        from pprint import pprint

        dllfinder = DllFinder(analysis.extensions)
        dlls = dllfinder.find_dlls()

        if dlls.missing:
            print('Missing DLLs')
            for name in sorted(dlls.missing):
                print('-', name)
            sys.exit(1)

        from .build_exe import ExeBuilder
        filename = join(self.dist, self.filename)
        exebuilder = ExeBuilder(filename=filename, analysis=analysis, subsystem=self.subsystem,
                                version=self.version, version_strings=self.version_strings,
                                extra=self.extra)
        exebuilder.build()

        self.copy_dlls(dlls)

    def prepare_dist_dir(self):
        """
        Make sure the dist directory exists and is empty.
        """
        if isdir(self.dist):
            # Windows won't allow us to delete a directory if it is a terminal's current
            # directory.  To make it easy to test, just clear the directory instead of deleting
            # it.
            self.logger.debug('emptying existing dist directory')
            for filename in os.listdir(self.dist):
                fqn = join(self.dist, filename)
                if isdir(fqn):
                    shutil.rmtree(fqn)
                else:
                    os.unlink(fqn)
        else:
            self.logger.debug('creating dist directory')
            os.makedirs(self.dist)

        # I've been having problems with corrupted executables.  Perhaps the directory
        # is not getting cleaned out properly?
        assert not list(os.listdir(self.dist))


    def copy_dlls(self, dlls):
        for f in dlls.found:
            self.logger.log(1, '%s --> %s', f, self.dist)
            shutil.copy(f, self.dist)
