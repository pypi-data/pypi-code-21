import os, shutil

class Dataset(object):
    """
    Instances of the Dataset class represent IPTK datasets on disk. A valid 
    path must be passed to the instance upon creation. An IPTK dataset will be
    created at the given path if it does not exist already.
    """
    def __init__(self, path):
        super(Dataset, self).__init__()
        self.path = path
        self.initialize()
    
    @property
    def data_path(self):
        return os.path.join(self.path, 'data')
    
    def initialize(self):
        """
        Initializes the dataset by creating an empty IPTK dataset structure
        including the data/, temp/, and meta/ directories. After 
        initialization, the dataset can be edited until it is locked by a call
        to the lock() method or the removal of the temp/ directory.
        Initializing an existing dataset is a no-op.
        """
        if not os.path.exists(self.data_path):
            subdirs = ["temp", "data", "meta"]
            for s in subdirs:
                os.makedirs(os.path.join(self.path, s), exist_ok=True)
        
    def lock(self):
        """
        Locks the dataset. Locked datasets can be used as job inputs but the
        content of their data/ directory must remain unchanged. A locked 
        dataset is indicated by the absence of a temp/ subdirectory. Unlocking
        a dataset by re-creating temp/ is not allowed and may lead to 
        unpleasant side effects. Locking a locked dataset is a no-op.
        """
        tmp_dir = os.path.join(self.path, 'temp')
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
    
    