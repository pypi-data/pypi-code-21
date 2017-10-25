
import sys, logging, shutil, zipfile, time, os
import marshal
from os.path import dirname, join, exists, abspath, isdir, isabs
from io import BytesIO
from py_compile import compile


class ExeBuilder:
    def __init__(self, logger=None, version_strings=None, extra=None, *, filename, version,
                 analysis, subsystem):
        """
        filename
          The fully qualified name of the executable to build.  The directory must already
          exist.

        extra
          An optional sequence of additional files (not Python source) to add to the
          executable.  Each element can be a relative path or a tuple pair containing
          (filename, archivename) where `archivename` is the name to store the file as in the
          executable.
        """
        if subsystem not in ('console', 'windows'):
            raise ValueError('subsystem must be "windows" or "console"')

        assert isdir(dirname(filename))

        self.filename = filename
        self.analysis = analysis
        self.subsystem = subsystem
        self.extra = extra
        self.version = version
        self.version_strings = version_strings

        self.logger = logger or logging.getLogger('kelvin')

    def build(self):
        fqn = self.get_src_exe()
        self.logger.debug('Copying %s to %s', fqn, self.filename)
        shutil.copy(fqn, self.filename)

        # I seem to be getting the wrong file sometimes.
        assert _copied(fqn, self.filename)

        from .resources import AddVersionResource
        AddVersionResource(self.filename, self.version, self.version_strings)

        # Append the Python modules and extra files to the executable.

        fd = open(self.filename, 'ab')
        fd.write(self.zip_files())
        fd.close()

    def zip_files(self):
        """
        Zips Python modules and returns the content.
        """
        buffer = BytesIO()
        zf = zipfile.ZipFile(buffer, mode='w', compression=zipfile.ZIP_DEFLATED)

        timestamp = int(time.time())

        ext = '.pyc'

        tempdir = dirname(self.filename)

        for m in self.analysis.modules:
            # Python creates its own __main__, which keep us from being able to import the real
            # one using that name.  Package the main module under the name __kelvinmain__.

            name = m.__name__ == '__main__' and '__kelvinmain__' or m.__name__

            if m.__file__.endswith('__init__.py'):
                arcname = join(name.replace('.', '/'), '__init__{}'.format(ext))
            else:
                arcname = name.replace('.', '/') + ext

            bytes = self._byte_compile(name, m.__file__, timestamp, tempdir)
            self.logger.log(1, 'storing %s bytes as %s', len(bytes), arcname)

            zf.writestr(arcname, bytes)

        # Now add extra files.  (Need to rearrange the modules here.)

        if self.extra:
            for item in self.extra:
                if isinstance(item, tuple):
                    filename, arcname = item
                else:
                    # The item is a single string which will be used for both the source filename and the archive name.
                    # The name must be a relative path since we don't know now to make the archive name ourselves.

                    if isabs(item):
                        raise Exception('extra file "{}" needs to be a relative path or the relative path in the zip must be provided'.format(item))

                    filename, arcname = item, item

                if not exists(filename):
                    raise Exception('extra file "{}" not found'.format(filename))

                arcname = arcname.replace('\\', '/')

                zf.write(filename, arcname)

        zf.close()

        return buffer.getvalue()

    def get_src_exe(self):
        """
        Find the executable we will copy and modify.
        """
        # When packaged as a binary wheel, the kelvinc.exe and kelvinw.exe files are in a data
        # directory at the root.

        root = dirname(abspath(__file__))

        assert self.subsystem in ('console', 'windows')
        filename = 'kelvin{}.exe'.format(self.subsystem[0])

        path = join(root, 'data', filename)
        if exists(path):
            return path

        # If we are working on Kelvin, such as using "pip --edit kelvin", grab the latest build
        # from the distutils build directory.

        build = self._find_build_dir()
        if build:
            path = join(build, 'data', filename)
            if exists(path):
                self.logger.debug('exepath=%s', path)
                return path
            self.logger.debug('exe not found: %s', path)

        raise Exception('{} not found.  Run setup.py build or install'.format(filename))

    def _find_build_dir(self):
        # distutils really sucks.  I need to know where the executables were built, but other
        # than creating a fake distutils.dist instance, I don't see how we can find the
        # directory.  We'll copy the same logic and hope it doesn't change much.
        #
        # This is only used for the development of Kelvin, so I'm not worried about it handling
        # every possibility.

        try:
            from distutils import util
        except:
            return None

        plat_name = util.get_platform()
        lib = "lib.%s-%d.%d" % (plat_name, *sys.version_info[:2])

        fqn = abspath(join(dirname(__file__), '..', 'build', lib, 'kelvin'))
        if not exists(fqn):
            self.logger.debug('libdir does not exist %s', fqn)
            return None

        self.logger.debug('libdir=%s', fqn)
        return fqn


    def _byte_compile(self, name, path, timestamp, tempdir):
        """
        Byte compiles a Python file and returns the bytes.

        path
        The path to the original source
        """

        # As of Python 3.6, there isn't an API to do this without writing to a physical file by
        # giving it a pathname.  We'll use a temp file - this is going to be kind of slow.
        #
        # I can't use any of the secure functions in tempfile since they all create the file, but
        # py_compile doesn't allow that.  We'll just make something in the dist directory and then
        # delete it.

        cfile = join(tempdir, 'temp.pyc')
        if exists(cfile):
            os.unlink(cfile)

        self.logger.log(1, 'compile: %s --> %s', path, cfile)

        try:
            compile(path, cfile=cfile, optimize=1)
        except Exception as details:
            raise Exception("compiling '%s' failed\n    %s: %s" % (path, details.__class__.__name__, details))

        # If a compilation error occurred, the error will have been written to the screen.
        if not exists(cfile):
            sys.exit('A compilation error occurred')

        b = open(cfile, 'rb').read()
        os.unlink(cfile)
        return b


def _copied(src, dst):
    """
    A debugging function used in an assertion to make sure the source file was successfully
    copied to the destination.
    """
    ss = os.stat(src)
    ds = os.stat(dst)

    if ss.st_size != ds.st_size:
        raise AssertionError('src=%s (%s) dst=%s (%s)' % (src, ss.st_size, dst, ds.st_size))

    return True
