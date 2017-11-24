import os
from typing import List

import yaml

def dict_updater(source: dict, dest: dict) -> dict:
    """
    Updates source dict with target dict values creating
    new dict and returning it
    """
    target = dest.copy()

    for k, v in source.items():
        if isinstance(v, dict) and k in dest:
            target[k] = dict_updater(v, dest[k])
        else:
            target[k] = v
    return target


class Object():
    pass


class ObjectFactory():

    def __init__(self, d:dict):
        self.d = d

    def create(self):
        obj = Object()
        for k, v in self.d.items():
            if isinstance(v, dict):
                obj.__dict__[k] = ObjectFactory(v).create()
            else:
                obj.__dict__[k] = v
        return obj


class SettingsObjectFactory():

    def __init__(self, settings:dict):
        self.settings = settings

    def get_settings(self, env:str):
        common_settings = self.settings.get('common', {})
        env_specific_settings = self.settings[env]

        env_settings = dict_updater(env_specific_settings, common_settings)
        return ObjectFactory(env_settings).create()


def create(env:str, settings:str, secrets:dict=None):
    """
    Creates setting object, which has properties from the settings file.
    secrets dict can contain environment specific secrets, which are updated to
    settings.
    """
    with open(settings, 'rt') as f:
        settings_data = yaml.load(f.read())
    if secrets and env in secrets:
        with open(secrets[env], 'rt') as f:
            secret_data = yaml.load(f.read())
        env_settings_with_secrets = dict_updater(secret_data, settings_data[env])
        settings_data[env] = env_settings_with_secrets

    return SettingsObjectFactory(settings_data).get_settings(env)


