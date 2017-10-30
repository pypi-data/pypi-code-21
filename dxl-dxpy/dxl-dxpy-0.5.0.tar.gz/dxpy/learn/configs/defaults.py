from dxpy.filesystem.path import Path
from dxpy.configs.base import Configs
from ruamel.yaml import YAML


def save():
    return {'frequency': 100, 'method': 'step'}


def load():
    return {'is_load': True, 'step': -1}


def model_filesystem():
    return {'path_model': './model', 'ckpt_name': 'save'}


def train():
    return {'model_fs': model_filesystem(),
            'load': load(),
            'save': save()}
