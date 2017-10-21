from .dataset_store import DatasetStore

class Runner(object):
    """docstring for Runner"""
    def __init__(self, dataset_root="/nps/datasets"):
        super(Runner, self).__init__()
        self.store = DatasetStore(dataset_root)
        
    def process_dataset(self, dataset_id):
        return self.store.get_dataset(dataset_id)
