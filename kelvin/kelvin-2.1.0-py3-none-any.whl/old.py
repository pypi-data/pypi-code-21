
import sys, os, zipfile, re, zipfile, tempfile
from os.path import abspath, basename, dirname, join, splitext, isdir, exists, isabs
import modulefinder, time
from distutils.core import Command
from distutils.errors import *
from distutils.util import get_platform
from distutils.file_util import copy_file
import py_compile, marshal, shutil
from .imageutils import find_dependencies
from . import resources

ispython3 = sys.version_info[0] >= 3

if ispython3:
    from . import compat3 as compat
else:
    import compat2 as compat

DEFAULT_WINDOWS_DLL_EXCLUDES = """
    oleaut32.dll user32.dll kernel32.dll wsock32.dll advapi32.dll ws2_32.dll ole32.dll odbc32.dll
    """

DEFAULT_WINDOWS_MODULE_EXCLUDES = ("""
    _dummy_thread _dummy_threading _emx_link _emx_link _gestalt _posixsubprocess ce ce doctest
    doctest fcntl fcntl grp java.lang org.python.core org.python.core os.path os.path os2 os2
    os2emxpath os2emxpath posix posix posixpath posixpath pwd pydoc readline riscos riscos
    riscosenviron riscosenviron riscospath riscospath rourl2path sitecustomize termios unittest
    usercustomize vms_lib win32api win32con win32pipe
    """ +

    # Module finder believes the following are modules and cannot import them so they are excluded by default.
    """
    ctypes._SimpleCData
    xml.dom.EMPTY_NAMESPACE xml.dom.EMPTY_PREFIX xml.dom.Node xml.dom.XMLNS_NAMESPACE xml.dom.XML_NAMESPACE
    """)

class FreezeCommand(Command):

    description = "Freezes Python scripts into Windows executables"

    user_options = [
        ('script=',                  's',  'the startup script'),
        ('subsystem=',               None, '"console" or "windows"'),
        ('includes=',                'i',  'comma and/or whitespace separated list of modules to include'),
        ('excludes=',                'e',  'comma and/or whitespace separated list of modules to exclude'),
        ('dll-excludes=',            None, 'comma and/or whitespace separated list of modules to exclude'),
        ('report=',                  'r',  'generate a ModuleFinder report with the given debug level'),
        ('disable-default-excludes', None, 'Disable deafult Windows module and DLL excludes'),
        ('dist-dir=',                None, 'directory to copy executable and DLLs to; defaults to dist'),
        ('version-strings=',         None, 'strings to add to version resource: {lang : {name: value, ...}}'),
        ('extra=',                   None, 'extra files to include in the app') ]

    CODEPAGE_UCS2LE = 0x04B0

    def initialize_options(self):
        self.script                   = None
        self.subsystem                = None
        self.includes                 = None
        self.excludes                 = None
        self.dll_excludes             = None
        self.report                   = None
        self.build_lib                = None
        self.build_temp               = None
        self.disable_default_excludes = None
        self.dist_dir                 = 'dist'
        self.version_strings          = None
        self.exe_path                 = None
        self.extra                    = None


    def finalize_options(self):
        if not self.script:
            raise DistutilsSetupError('missing "script" option')

        if self.subsystem not in ('console', 'windows'):
            raise DistutilsSetupError('Must set subsystem to "console" or "windows"')

        self.includes     = str2list(self.includes)
        self.excludes     = str2list(self.excludes)
        self.dll_excludes = str2list(self.dll_excludes)
        self.report       = int(self.report or 0)

        self.dist_dir = abspath(self.dist_dir)

        plat_name = get_platform()
        plat_specifier = ".%s-%s" % (plat_name, sys.version[0:3])

        if not self.build_lib:
            self.build_lib = join('build', 'lib' + plat_specifier)

        if not self.build_temp:
            self.build_temp = join('build', 'temp' + plat_specifier)

        if not self.disable_default_excludes:
            self.excludes     += str2list(DEFAULT_WINDOWS_MODULE_EXCLUDES)
            self.dll_excludes += str2list(DEFAULT_WINDOWS_DLL_EXCLUDES)

        if not self.exe_path:
            self.exe_path = join(self.dist_dir, splitext(basename(self.script))[0] + '.exe')

        if not self.version_strings:
            self.version_strings = { 0x0409 : {} }

        if self.version_strings:
            if not isinstance(self.version_strings, dict):
                raise DistutilsOptionError('version-strings must be a dictionary')
            # The key should be a DWORD for the language (e.g. 0x0409 for English).  The value should be a list of
            # (name, value) pairs.

            # Poke in the values we know if they are not provided.
            md = self.distribution.metadata

            map_metadata = [('ProductName',     'name'),
                            ('ProductVersion',  'version'),
                            ('FileVersion',     'version'),
                            ('FileDescription', 'description')]

            for lang, strings in self.version_strings.items():
                for name, attr in map_metadata:
                    if name not in strings and getattr(md, attr, None):
                        strings[name] = getattr(md, attr)

                strings['OriginalFilename'] = basename(self.exe_path)

        if self.extra:
            # Make sure that each entry is either a string or a tuple of (path, archive-path) strings.
            #
            # Note that we wont determine if the files exist just yet.  I'm not sure when the parsing takes place and
            # we want to give the user time to create the files if necessary.
            if not isinstance(self.extra, list):
                raise DistutilsOptionError('The extra option must be a list')

            for item in self.extra:
                if not compat.istext(item):
                    if not isinstance(item, tuple) or len(item) != 2 or not all(compat.istext(i) for i in item):
                        raise DistutilsOptionError('Extra values must be strings or a tuple containing (file-path, zip-path): found=%s' % repr(item))

        else:
            self.extra = []

    def run(self):
        if not isdir(self.dist_dir):
            os.makedirs(self.dist_dir)

        # Analyze dependencies

        modules, dlls = self.analyze()

        # Create the executable.
        #
        # Note that you must add resources before appending the zip file.

        shutil.copyfile(self.get_src_exe(), self.exe_path)

        # Add the version as a resource.

        resources.AddVersionResource(self.exe_path, self.distribution.metadata.version, self.version_strings)

        # Append the Python modules and extra files to the executable.

        fd = open(self.exe_path, 'ab')
        fd.write(self.zip_files(modules))
        fd.close()

        # Copy extensions and DLLs to the dist directory.

        # self.verbose defaults to 1, which stinks (in my opinion).  Shell commands should be
        # silent unless you ask for output.  Therefore, we'll only set the copy verbosity if
        # self.verbose > 1.  (Put this somewhere at the top of the file or in a hacking
        # document.)

        for dll in dlls:
            copy_file(dll, join(self.dist_dir, basename(dll)),
                      verbose=(self.verbose > 1))


    def get_src_exe(self):
        root = dirname(abspath(__file__))

        filename = (self.subsystem.lower() == 'console') and 'kelvinc.exe' or 'kelvinw.exe'

        path = join(root, 'data', filename)
        if exists(path):
            return path

        # If running from the test directory, return the copy in kelvin/build/lib-x.x directory
        # to make testing easy.

        path = join(root, '..', self.build_lib, 'kelvin', 'data', filename)
        if exists(path):
            return path

        raise DistutilsError('{} not found.  Run setup.py build or install'.format(filename))


    def zip_files(self, modules):
        """
        Zips Python modules and returns the content.
        """
        buffer = compat.BytesIO()
        zf = zipfile.ZipFile(buffer, mode='w', compression=zipfile.ZIP_DEFLATED)

        timestamp = int(time.time())

        for m in modules:

            # Python creates its own __main__, which keep us from being able to import the real
            # one using that name.  Package the main module under the name __kelvinmain__.

            name = m.__name__ == '__main__' and '__kelvinmain__' or m.__name__

            if m.__file__.endswith('__init__.py'):
                arcname = join(name.replace('.', '/'), '__init__.pyo')
            else:
                arcname = name.replace('.', '/') + '.pyo'

            bytes = _byte_compile(name, m.__file__, timestamp)

            zf.writestr(arcname, bytes)

        # Now add extra files.  (Need to rearrange the modules here.)

        for item in self.extra:
            if isinstance(item, tuple):
                filename, arcname = item
            else:
                # The item is a single string which will be used for both the source filename and the archive name.
                # The name must be a relative path since we don't know now to make the archive name ourselves.

                if isabs(item):
                    raise DistutilsError('extra file "{}" needs to be a relative path or the relative path in the zip must be provided'.format(item))

                filename, arcname = item, item

            if not exists(filename):
                raise DistutilsError('extra file "{}" not found'.format(filename))

            arcname = arcname.replace('\\', '/')

            zf.write(filename, arcname)

        zf.close()

        return buffer.getvalue()


    def analyze(self):
        """
        Analyzes the script and returns (modules, dlls), a list of Python modules and a list of
        DLLs (extensions and all dependencies).

        Each element of modules is a modulefinder.Module object.  Each element of dlls is a
        fully-qualified path to the DLL.
        """
        if self.verbose >= 2:
            print('Searching for imported modules')

        # Find all modules used by the startup script and includes.

        from modulefinder import ReplacePackage
        ReplacePackage("_xmlplus", "xml")

        finder = modulefinder.ModuleFinder(
            excludes=self.excludes,
            debug=self.report)
        finder.run_script(self.script)
        for module in self.includes:
            finder.import_hook(module)

        # Add __kelvin__, our startup module.

        fqn = join(dirname(abspath(__file__)), '__kelvin__.py')
        finder.load_file(fqn)

        if self.report:
            finder.report()

        # If a package is imported, include all of its files.  (We'll need an exception for
        # codecs, I think.)

        self.expand_packages(finder)

        modules, extensions, missing, maybe = self.parse_mf_results(finder)

        if self.verbose >= 2:
            print('Searching for DLL dependencies')

        founddlls, missingdlls = self.find_dlls(extensions)

        if missing or maybe:
            print('The following modules could not be found:')
            for module in sorted(list(missing) + list(maybe)):
                print(' ', module)

        if missingdlls:
            print('The following DLLs could not be found:')
            for dll in sorted(missingdlls):
                print(' ', dll)

        dlls = set(item.__file__ for item in extensions) | set(founddlls)

        return modules, dlls


    def expand_packages(self, finder):
        """
        For each package included, include all modules under the package.

        Subpackages are also included.
        """
        packages = [ m for m in finder.modules.values() if m.__path__ ]

        existing = set(m.__file__ for m in finder.modules.values() if m.__file__)

        # Module('testmod', 'C:\\bin\\python32\\lib\\site-packages\\testmod\\__init__.py', ['C:\\bin\\python32\\lib\\site-packages\\testmod'])
        # Module('testmod.test1', 'C:\\bin\\python32\\lib\\site-packages\\testmod\\test1.py')

        for package in packages:
            # REVIEW: Why is __path__ a list?  Can there be more than one?
            for root in package.__path__:
                prefixlen = len(dirname(root)) + 1

                for dirpath, dirnames, filenames in os.walk(root):

                    filenames = [f for f in filenames if f.endswith('.py')]

                    if not filenames:
                        del dirnames[:]
                        continue

                    for filename in filenames:
                        fqn = join(dirpath, filename)
                        
                        if filename == '__init__.py':
                            # If the __init__.py is for a subpackage, we need it.  If it is for the top-level package,
                            # we already have it since it is how we got here.
                            if dirpath == root:
                                continue
                            
                            # Do not include the __init__ in the module name - it should just be the package name.
                            name = dirname(fqn)[prefixlen:].replace('\\', '.')

                        else:
                            # The name is the package plus the module.
                            name = fqn[prefixlen:-3].replace('\\', '.')

                        if name not in finder.modules:
                            finder.modules[name] = modulefinder.Module(name, fqn)


    def parse_mf_results(self, finder):
        modules    = []
        extensions = []

        for item in finder.modules.values():
            src = item.__file__
            if not src:
                # Part of Python
                continue

            base, ext = splitext(src)

            if ext in ['.py', '.pyc', '.pyo']:
                modules.append(item)
                continue

            if ext == '.pyd':
                extensions.append(item)
                continue

            raise DistutilsInternalError('Do not know how to handle {!r}'.format(src))

        missing, maybe = finder.any_missing_maybe()

        missing.extend(finder.badmodules.keys())

        # I don't know why (yet), but finder puts things into badmodules even though they are
        # supposed to be excluded.  We'll manually remove them until we get to the bottom of
        # this.
        missing = set(missing) - set(self.excludes)

        return modules, extensions, missing, maybe


    def find_dlls(self, extensions):
        """
        Finds the DLLs imported by (needed by) the extensions.

        extensions
          A list of modulefinder.Module objects for the Python extension DLLs.
        """
        path = [ dirname(sys.executable) ]
        path.extend(os.environ['PATH'].split(';'))
        path.extend(sys.path)
        path = ';'.join(path)

        images = [ sys.executable ] # picks up python DLL
        images.extend(item.__file__ for item in extensions)

        map_module_to_path = {}

        for image in images:
            map_module_to_path.update(find_dependencies(image, path))

        # Remove excluded DLLs.

        exclude = set(e.lower() for e in self.dll_excludes)

        # Separate the missing and found.

        found = [ fqn for (module, fqn) in map_module_to_path.items() if module not in exclude and fqn is not None ]

        missing = [ module for (module, fqn) in map_module_to_path.items() if module not in exclude and fqn is None ]

        return found, missing


def str2list(value):
    value = value and value.strip() or None
    if not value:
        return []
    return re.split(r'[, \t\r\n]+', value)


def _byte_compile(name, path, timestamp):
    """
    Byte compiles a Python file and returns the bytes.

    This is copied from py_compile and is risky, but py_compile
    doesn't support a version that writes to a file object.
    """
    text = open(path, 'U').read()
    try:
        if ispython3:
            code = compile(text, path, 'exec', optimize=1)
        else:
            if sys.flags.optimize != 1:
                raise DistutilsError('Optimize is set to {}.  Run python with -O flag to set optimize to 1.'.format(sys.flags.optimize))

            code = compile(text, path, 'exec')

    except Exception as details:
        raise DistutilsError("compiling '%s' failed\n    %s: %s" % (path, details.__class__.__name__, details))

    b = compat.BytesIO()
    b.write(py_compile.MAGIC)
    py_compile.wr_long(b, timestamp)
    b.write(marshal.dumps(code))
    return b.getvalue()
