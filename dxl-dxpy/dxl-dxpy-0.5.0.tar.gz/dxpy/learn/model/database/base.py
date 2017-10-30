from ..graph import Graph
import numpy as np


class Database(Graph):
    """Base class of database
    Database add some special tasks based on graph:
        1. load single
        2. load batch
        3. load next N samples (given N)
        4. load next N samples with batch (given N)
    """

    def __init__(self, name):
        super(__class__, self).__init__(name)

    def load_single(self, feed_dict=None, name=None):
        raise NotImplementedError

    def load_batch(self, feed_dict=None, name=None):
        result = np.zeros(self.c['batch_shape'])
        for _ in range(self.c['batch_size']):
            pass

    def load_N(self, feed_dict=None, name=None):
        raise NotImplementedError

    def load_N_batch(self, feed_dict=None, name=None):
        raise
