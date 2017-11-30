import os
import yaml
import pytest

@pytest.fixture
def i18n_config():
    fname = os.path.join(os.path.dirname(__file__), 'i18n_config.yml')
    with open(fname) as info:
        info_dict = yaml.load(info)
        return info_dict