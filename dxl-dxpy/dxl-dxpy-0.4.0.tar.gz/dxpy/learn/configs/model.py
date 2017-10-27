from dxpy.filesystem.path import Path
from dxpy.configs.base import Configs
from ruamel.yaml import YAML


class ConfigsSave(Configs):
    _names = ('frequency', 'method')
    _default_configs = {
        'frequency': 100,
        'method': 'step'
    }

    def __init__(self, **kwargs):
        super(__class__, self).__init__(**kwargs)


class ConfigsLoad(Configs):
    _names = ('is_load', 'step')
    _default_configs = {
        'is_load': True,
        'step': -1
    }

    def __init__(self, **kwargs):
        super(__class__, self).__init__(**kwargs)


class ConfigsModelFS(Configs):
    _names = ('path_model', 'ckpt_name')
    _default_configs = {
        'path_model': './model',
        'ckpt_name': 'save'
    }

    def __init__(self, **kwargs):
        super(__class__, self).__init__(**kwargs)


class ConfigsTrain(Configs):
    _names = ('model_fs', 'load', 'save')
    _default_configs = {
        'model_fs': ConfigsModelFS(),
        'load': ConfigsLoad(),
        'save': ConfigsSave()
    }

    def __init__(self, **kwargs):
        super(__class__, self).__init__(**kwargs)


from dxpy import serialization
serialization.register(ConfigsSave)
serialization.register(ConfigsLoad)
serialization.register(ConfigsModelFS)
serialization.register(ConfigsTrain)
