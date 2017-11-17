# -*- coding: utf-8 -*-
# Author: heheqiao <614400597@qq.com>


class InstallFailedException(Exception):
    """Exceptions raised when `pip.main` failed
    """
    def __init__(self, package):
        """Initialize

        Args:
            package: a `str`
        """
        self.package = package

    def __str__(self):
        return 'Pip install {} failed!'.format(self.package)


class ProjectGenerationError(Exception):
    """Exceptions raised when files not found in path
    """
    def __init__(self, file_path):
        """Initialize

        Args:
            file_path: a `str`
        """
        self.file_path = file_path

    def __str__(self):
        return 'Generation of {} failed'.format(self.file_path)
