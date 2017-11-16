import contextlib
import os
import platform
import re
import sys

if sys.version_info < (3,1):
    from mock import patch, Mock
else:
    from unittest.mock import patch, Mock

class AutoAttr:
    def __call__(self, *args, **kwargs):
        pass
    def __getattr__(self, attr):
        return self

@contextlib.contextmanager
def patched_tecplot_module():
    patches = []

    # patch for all platforms
    patches.append(patch('ctypes.cdll.LoadLibrary',
                         Mock(return_value=AutoAttr())))

    # patch for darwin
    if platform.system() == 'Darwin':
        from ctypes.util import find_library
        find_library_orig = find_library
        def find_library_mock(name):
            if re.search(r'tecutilbatch', name):
                return '/path/to/file'
            else:
                return find_library_orig(name)
        patches.append(patch('ctypes.util.find_library',
                                  Mock(side_effect=find_library_mock)))

    # patch for windows
    if platform.system() == 'Windows':
        path_exists_orig = os.path.exists
        def path_exists_mock(name):
            if re.search(r'tecutilbatch', name):
                return True
            else:
                return path_exists_orig(name)
        patches.append(patch('os.path.exists',
                                  Mock(side_effect=path_exists_mock)))

    for p in patches:
        p.start()

    yield patches

    for p in patches:
        p.stop()

def patch_tecplot_module():
    with patched_tecplot_module():
        import tecplot
        tecplot.sdk_version_info = (9999, 9999, 9999)
