import os
import json
from ..const import IT_MAP

def get_cfg_path():
    usr_home = os.path.expanduser('~')
    cfg_dir = os.path.join(usr_home, '.batchcompute')
    if(not os.path.exists(cfg_dir)):
        os.makedirs(cfg_dir)
    cfg_path = os.path.join(cfg_dir, 'clicache_ecs_instancetypes.json')
    return cfg_path


def get():
    cfg_path = get_cfg_path()

    if(os.path.exists(cfg_path)):
        with open(cfg_path, 'r') as f:
            obj = json.loads(f.read())
            for k,v in IT_MAP.items():
                obj[k] = v
            return obj
    else:
        return IT_MAP

def save(m):
    cfg_path = get_cfg_path()
    with open(cfg_path, 'w') as f:
        f.write(json.dumps(m))
