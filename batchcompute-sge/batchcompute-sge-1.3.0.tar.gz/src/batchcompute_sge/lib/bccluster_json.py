
import json
import os

CONFIG_NAME = '.bccluster.json'

def get_config_path():
    """
    get config path,
    usually it should be /root/.bccluster.json
    """
    usr_home = os.path.expanduser('~')
    cfg_path = os.path.join(usr_home, CONFIG_NAME)
    return cfg_path


def save(obj):
    cfg_path = get_config_path()
    with open(cfg_path, 'w') as f:
        f.write(json.dumps(obj, indent=2, skipkeys=' '))


def get():
    cfg_path = get_config_path()
    try:
        with open(cfg_path, 'r') as f:
            obj = json.loads(f.read())
    except Exception as e:
        obj = {}
    return obj

def get_required_login():
    cfg_path = get_config_path()
    try:
        with open(cfg_path, 'r') as f:
            obj = json.loads(f.read())

    except Exception as e:
        obj = {}
    if not obj.get('access_key_id'):
        raise Exception('you need to login first')

    return obj