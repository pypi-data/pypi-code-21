import json
import os

import click

config_path = os.path.abspath(__file__)
config_dir = os.path.dirname(config_path)


class Config:
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            new = super(Config, cls).__new__(cls)
            cls.instance = new
            return new
        else:
            return cls.instance

    def __init__(self):
        with open(os.path.join(config_dir, 'config.json'), 'r') as f:
            config = json.load(f)

        for attr, value in config.items():
            setattr(self, attr, value)

    def save(self):
        with open(os.path.join(config_dir, 'config.json'), 'w') as f:
            json.dump(self.__dict__, f)
