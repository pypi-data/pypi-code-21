
import sys, os, re, logging
from os.path import dirname, basename, isabs, join, abspath, exists
from collections import namedtuple
from .imageutils import find_dependencies

DllList = namedtuple('DllList', 'found missing')

WHITELIST = re.compile(r'(api-ms|vcruntime|ucrtbase)')

class DllFinder:
    def __init__(self, extensions, exclude=None, logger=None):
        self.extensions = extensions
        self.exclude = exclude
        self.logger = logger or logging.getLogger('kelvin.dlls')

        self.windir = os.environ['WINDIR'].lower()

    def find_dlls(self):
        """
        Finds the DLLs imported by (needed by) the extensions.

        extensions
          A list of modulefinder.Module objects for the Python extension DLLs.
        """
        path = [ dirname(sys.executable) ]
        path.extend(os.environ['PATH'].split(';'))
        path.extend(sys.path)
        path = ';'.join(path)

        self.logger.log(1, 'DLL search path: %s', path)

        map_module_to_path = {}

        images = [sys.executable]  # picks up python DLL

        fqn = _find_file('ucrtbase.dll', path)
        if not fqn:
            logger.error('Unable to find ucrtbase.dll.  Not all DLLs may be found!')
        else:
            images.append(fqn)
            map_module_to_path[basename(fqn)] = fqn

        # Include any extensions, which are DLLs, that the analyzer found we need.
        # Include in the list of DLLs to copy (map_module_to_path) and also in the
        # list of images to look for dependencies for (images).

        for item in self.extensions:
            images.append(item.__file__)
            map_module_to_path[basename(item.__file__)] = item.__file__

        seen = set()
        # The images we've already processed, as fully qualified paths.  The same as the values
        # in map_module_to_path.

        while images:
            image = images.pop(0)
            assert isabs(image), 'Not absolute path: {}'.format(image)

            dep = find_dependencies(image, path)
            self.logger.log(1, 'Dependencies: image=%s deps=%r', image, dep)

            for filename, fqn in dep.items():
                if fqn in seen:
                    continue
                seen.add(fqn)

                if self._exclude(fqn):
                    self.logger.debug('Excluding DLL %s', fqn)
                    continue

                images.append(fqn)
                map_module_to_path[filename] = fqn

        # Separate the missing and found.

        found = list(map_module_to_path.values())

        # TODO: Do we know when a DLL is missing now?
        # missing = [ module for (module, fqn) in map_module_to_path.items() if module not in exclude and fqn is None ]
        missing = []

        return DllList(found, missing)

    def _exclude(self, fqn):
        """
        Returns True if this DLL should be excluded.  We need to exclude during processing
        so we don't pick up dependencies of an excluded DLL.
        """
        fqn = fqn.lower()

        filename = basename(fqn)

        # Always include pyd files unless they have been explicitly excluded.  (I don't think
        # this can happen, but there is no since in making it impossible.)
        if self.exclude and filename.endswith('.pyd'):
            return filename[:-4] in self.exclude

        if WHITELIST.match(filename):
            return False

        if fqn.startswith(self.windir):
            return True

        return False


def _find_file(filename, path):
    """
    Searches for the given filename in the path string.  If found, returns the absolute path.
    Otherwise returns None.
    """
    for dir in path.split(';'):
        fqn = join(abspath(dir), filename)
        if exists(fqn):
            return fqn
    return None
