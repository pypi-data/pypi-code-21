from dxpy.configs import Configs

from .dataset import Dataset


class ConfigsMNISTDataset(Configs):
    _names = ('path', 'batch_size')
    _default_configs = {'batch_size': 32}


class MNIST(Dataset):
    def __init__(self, config):
        super(__class__, self).__init__(config)
