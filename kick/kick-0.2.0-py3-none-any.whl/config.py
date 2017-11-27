import shutil
import inspect
import pathlib

import toml
import addict
from first import first

CONFIGDIR = pathlib.Path.home() / '.config'


def get_caller_path():
    stack = inspect.stack()
    try:
        frame = first(stack, key=lambda frame: 'kick.' in (frame.code_context[0] or ['']))
        path = pathlib.Path(frame.filename).parent
    except:
        path = None
    finally:
        del stack

    return path


def get_local_config_path(variant):
    local_dir = get_caller_path() or pathlib.Path('.')
    path = local_dir / 'config' / f'{variant}.toml'
    if not path.exists():
        path = local_dir / 'config' / f'config.toml'
    return path


def Config(name, path=None, variant='config'):
    config_path = CONFIGDIR / name / f'{variant}.toml'
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        local_config_path = path or get_local_config_path(variant)
        shutil.copy(local_config_path, config_path)

    config = addict.Dict(toml.loads(config_path.read_text()))
    return config


def update_config(name, path=None, variant='config'):
    config_path = CONFIGDIR / name / f'{variant}.toml'
    config = Config(name, path, variant)
    local_config = toml.loads((path or get_local_config_path(variant)).read_text())
    local_config.update(config)
    config_path.write_text(toml.dumps(local_config))
