import os
import shutil
import tempfile
from typing import Set, Tuple

import atexit


class TempManager:
    """
    Allows management of temp files and directories such that they can be easily removed after use.

    For use where using context managers to ensure removal is not possible.

    The manager will remove any remaining temp files upon (clean) exit.
    """
    def __init__(self, default_mkdtemp_kwargs: dict=None, default_mkstemp_kwargs: dict=None):
        """
        Constructor.
        :param default_mkdtemp_kwargs:
        :param default_mkstemp_kwargs:
        """
        self.default_mkdtemp_kwargs = default_mkdtemp_kwargs if default_mkdtemp_kwargs is not None else {}
        self.default_mkstemp_kwargs = default_mkstemp_kwargs if default_mkstemp_kwargs is not None else {}
        self._temp_directories = set()  # type: Set[str]
        self._temp_files = set()    # type: Set[str]
        atexit.register(self.tear_down)

    def tear_down(self):
        """
        Tears down all temp files and directories.
        """
        while len(self._temp_directories) > 0:
            directory = self._temp_directories.pop()
            shutil.rmtree(directory, ignore_errors=True)
        while len(self._temp_files) > 0:
            file = self._temp_files.pop()
            try:
                os.remove(file)
            except OSError:
                pass

    def create_temp_directory(self, **mkdtemp_kwargs) -> str:
        """
        Creates a temp directory.
        :param mkdtemp_kwargs: named arguments to be passed to `tempfile.mkdtemp`
        :return: the location of the temp directory
        """
        kwargs = {**self.default_mkdtemp_kwargs, **mkdtemp_kwargs}
        location = tempfile.mkdtemp(**kwargs)
        self._temp_directories.add(location)
        return location

    def create_temp_file(self, **mkstemp_kwargs) -> Tuple[int, str]:
        """
        Creates a temp file.
        :param mkstemp_kwargs: named arguments to be passed to `tempfile.mkstemp`
        :return: tuple where the first element is the file handle and the second is the location of the temp file
        """
        kwargs = {**self.default_mkstemp_kwargs, **mkstemp_kwargs}
        handle, location = tempfile.mkstemp(**kwargs)
        self._temp_files.add(location)
        return handle, location
