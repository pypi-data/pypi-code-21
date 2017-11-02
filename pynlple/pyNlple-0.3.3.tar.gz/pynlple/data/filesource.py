# -*- coding: utf-8 -*-
from pynlple.data.source import Source
from pynlple.exceptions import DataSourceException
from pynlple.module import is_folder, is_file, list_dir, append_paths


class FilePathSource(Source):
    """Class for providing filepaths from data folders."""

    def __init__(self, paths, extension_suffix=None):
        self.paths = paths
        self.extension = extension_suffix

    def get_files(self):
        accumulated_paths = list()
        for path in self.paths:
            if is_file(path):
                accumulated_paths.append(path)
            elif is_folder(path):
                files = list_dir(path)
                if self.extension:
                    for file in filter(lambda f: f.endswith(self.extension), files):
                        accumulated_paths.append(append_paths(path, file))
                else:
                    for file in files:
                        accumulated_paths.append(append_paths(path, file))
            else:
                raise DataSourceException('Path {0} does not exist/is neither file nor folder!'.format(path))
        return accumulated_paths

    def __iter__(self):
        for file_ in self.get_files():
            yield file_
