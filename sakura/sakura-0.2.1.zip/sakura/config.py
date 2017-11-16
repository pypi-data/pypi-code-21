import sys
_PY2 = sys.version_info[0] == 2

if _PY2:
    basestring = basestring
else:
    basestring = str


def init_config(config):
    if isinstance(config, basestring):
        with open(config, 'r') as f:
            content = f.read()
        import json
        config_dict = json.loads(content)
    elif isinstance(config, dict):
        config_dict = config
    else:
        config_dict = config.__dict__
    globals().update(config_dict)
