import pathlib
import shutil
from dxpy.file_system.path import Path


class FileSystem:
    @staticmethod
    def exists(path):
        if isinstance(path, str):
            path = Path(path)
        return pathlib.Path(path.abs).exists()

    @staticmethod
    def copy(path_target, path_source):
        raise NotImplementedError

    @staticmethod
    def move(path_target, path_source):
        raise NotImplementedError

    class File:
        @staticmethod
        def check(path):
            return pathlib.Path(path.abs).is_file()

        @staticmethod
        def create(path):
            # Get a emtpy file by FileFactory
            # Update file with content
            pathlib.Path(path.abs).touch()

        @staticmethod
        def delete(path):
            pathlib.Path(path.abs).unlink()

    class Directory:
        @staticmethod
        def check(path):
            return pathlib.Path(path.abs).is_dir()

        @staticmethod
        def create(path, parents=False):
            if isinstance(path, str):
                path = Path(path)
            return pathlib.Path(path.abs).mkdir(parents=parents)

        @staticmethod
        def delete(path):
            shutil.rmtree(path.abs)

        @staticmethod
        def glob(path, pattern='*'):
            return [str(x.absolute()) for x in pathlib.Path(path.abs).glob(pattern)]
