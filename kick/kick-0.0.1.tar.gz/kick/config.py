import shutil
import pathlib

import toml
import addict

CONFIGDIR = pathlib.Path.home() / '.config'


def Config(name, path):
    config_path = CONFIGDIR / name / 'config.toml'
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        local_config_path = path or pathlib.Path('config.toml')
        shutil.copy(local_config_path, config_path)

    config = addict.Dict(toml.loads(config_path.read_text()))
    return config
