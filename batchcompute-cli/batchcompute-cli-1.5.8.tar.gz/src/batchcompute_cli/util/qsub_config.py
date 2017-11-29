
import os
import json

def get():
    usr_home = os.path.expanduser('~')
    cfg_dir = os.path.join(usr_home, '.qsub-task-description.json')
    if (os.path.exists(cfg_dir)):
        with open(cfg_dir) as f:
            return json.loads(f.read())
    return {}
