import os
import mock

__OPEN_REF = None


def patch_open_read(files):
    """
    Patch open() command and mock read() results

    :type files: dict
    """
    files = {os.path.abspath(path): content for path, content in files.items()}

    def mock_open_wrapper(path, *args, **kwargs):
        __tracebackhide__ = True  # noqa

        assert path in files, 'try to open a non-mocked path\n    desired={desired!r}\n    mocked={mocked!r}'.format(
            desired=path, mocked=files.keys())

        open_mock = mock.mock_open(read_data=files[path])
        return open_mock(path, *args, **kwargs)

    return mock.patch(__get_open_ref(), mock_open_wrapper)


def __get_open_ref():
    """
    :rtype str
    """
    global __OPEN_REF

    if __OPEN_REF:
        return __OPEN_REF

    try:
        from builtins import open  # noqa: F401
        __OPEN_REF = 'builtins.open'
    except ImportError:
        from __builtin__ import open  # noqa: F401
        __OPEN_REF = '__builtin__.open'

    return __OPEN_REF
