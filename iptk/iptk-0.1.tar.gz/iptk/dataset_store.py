import os, re
from .dataset import Dataset

class DatasetStore(object):
    """Manages the storage and creation of datasets on disk"""
    def __init__(self, root_path):
        super(DatasetStore, self).__init__()
        self.root_path = root_path
    
    def get_dataset(self, dataset_id, create_ok=False):
        """
        Fetch a Dataset object backed by this DatasetStore. Raises a value
        error for invalid values of dataset_id. The dataset identifier must be
        a hex string of 40 characters (i.e. must match /^[0-9a-z]{40}$/). This
        method can optionally create an empty dataset if no dataset with the
        given identifier exists. 
        """
        if not re.match("^[0-9a-z]{40}$", dataset_id):
            raise ValueError('Invalid dataset identifier')
        subdir = "/".join(list(dataset_id[:4]))
        path = os.path.join(self.root_path, subdir, dataset_id)
        if not os.path.exists(path) and not create_ok:
            raise ValueError('No existing dataset at path and create_ok is False')
        return Dataset(path)
