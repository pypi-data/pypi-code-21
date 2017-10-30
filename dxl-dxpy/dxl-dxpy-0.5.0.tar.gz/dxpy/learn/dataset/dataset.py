from ..model.base import Net


def default_path():
    import os
    from dxpy.filesystem import Path, Directory
    path_env = os.environ.get('PATH_DATASETS')
    if path_env is not None:
        dataset_dir = Directory(Path(path_env))
        if dataset_dir.exists():
            return dataset_dir.path
    return None


class Dataset(Net):
    """
    Subnet for loading datasets.    
    """

    def __init__(self, name):
        super(__class__, name).__init__(self)

    def _initialize(self):
        pass

    def _finalize(self):
        pass

    def __enter__(self):
        self._initialize()

    def __exit__(self, type, value, traceback):
        self._finalize()

    def run(self, session=None, task=None, feeds=None):
        return self.batch()

    def single(self, session=None, task=None, feeds=None):
        pass

    def batch():
        pass


class DatasetHDF5(Net):
    def __init__(self, name):
        super(__class__, name).__init__(self)

    def run(self, session=None, task=None, feeds=None):
        pass
