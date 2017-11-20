'''Generic storage interfaces with a common api
   So far, only file-based interfaces are implemented (.json and .npy)
   '''

import os
import shutil
import numpy as np
from numpy.lib.npyio import _savez

try:
    import simplejson as json
except ImportError:
    import json

class StorageInterface(object):
    def __init__(self):
        pass

    def exists(self, name):
        pass

    def save(self, name, data):
        pass

    def load(self, name):
        pass

def _create_tmp(filepath):
    '''Change something.ext into something.tmp.ext'''
    return '{}.tmp{}'.format(*os.path.splitext(filepath))

class FileBasedStorageInterface(StorageInterface):
    def __init__(self, file_ext, metrics_dir):
        self.file_ext = file_ext
        self.metrics_dir = metrics_dir
        StorageInterface.__init__(self)

    def _get_filepath(self, name):
        '''Get the filename for any given metric'''
        return os.path.join(self.metrics_dir, name + self.file_ext)

    def exists(self, name):
        '''Test if a given metric already exists'''
        filepath = self._get_filepath(name)
        return os.path.exists(filepath)

    def _load(self, filepath):
        return None

    def _save(self, filepath, data):
        pass

    def load(self, name):
        filepath = self._get_filepath(name)
        return self._load(filepath)

    def save(self, name, data):
        filepath = self._get_filepath(name)
        tmp = _create_tmp(filepath)
        self._save(tmp, data)
        shutil.move(tmp, filepath)

# Json is a less-than-ideal storage format for binary data, but it's easy:
def _to_flat(x):
    return (x.tolist() if type(x) == np.ndarray else x)

class JsonStorageInterface(FileBasedStorageInterface):
    def __init__(self, metrics_dir):
        FileBasedStorageInterface.__init__(self, file_ext='.json', metrics_dir=metrics_dir)

    def _load(self, filepath):
        with open(filepath) as fid:
            return json.load(fid)

    def _save(self, filepath, data):
        with open(filepath, 'w') as fid:
            json.dump(_to_flat(data), fid)  # Force numpy arrays to lists

# Npy is a actually a great storage format for this:
class NpyStorageInterface(FileBasedStorageInterface):
    def __init__(self, metrics_dir):
        FileBasedStorageInterface.__init__(self, file_ext='.npy', metrics_dir=metrics_dir)

    def _load(self, filepath):
        return np.load(filepath)

    def _save(self, filepath, data):
        np.save(filepath, data)

class NpzStorageInterface(FileBasedStorageInterface):
    '''A StorageInterface that allows entries to include multiple arrays.

    Can store either a single array, a list of arrays, or a dictionary of arrays.
    This uses the metric data type to route the storage type, so ensure you
    pass an array instead of a list if you mean to store an array ;)
    '''
    def __init__(self, metrics_dir, compress=False, allow_pickle=False, list_limit=None):
        self.compress = compress
        self.allow_pickle = allow_pickle
        self.list_limit = list_limit
        FileBasedStorageInterface.__init__(self, file_ext='.npz', metrics_dir=metrics_dir)

    def _load(self, filepath):
        val = np.load(filepath, allow_pickle=self.allow_pickle)
        return (dict(val) if 'arr_0' not in val.files else  # Return dictionary
                val['arr_0'] if len(val.files) == 1 else    # Return singleton
                [val[k] for k in sorted(val.files)])        # Return list

    def _save(self, filepath, data):
        args, kwds = (([], data)                           # Use dictionary storage
                      if hasattr(data, 'keys') else
                      (data, {})                           # Use list storage
                      if isinstance(data, (list, tuple)) else
                      ([data], {}))                       # Use singleton storage
        if self.list_limit is not None and len(args) > self.list_limit:
            msg = 'Data violates list length limit! Use an array instead (or adjust the limit).'
            raise TypeError(msg)

        _savez(filepath, args, kwds, self.compress, self.allow_pickle)

# A storage interface could also work by storing a "document" version of a
# number of different metrics in a single file which would cut down on file
# usage, but make it harder to update with new metrics.
#
# class Np(y/z)ConsolidatedStorageInterface(StorageInterface)
# or
# class PyTablesStorageInterface(StorageInterface)

# And this might be a better way for some applications:
# class SQLStorageInterface(StorageInterface)

if __name__ == '__main__':
    pass
