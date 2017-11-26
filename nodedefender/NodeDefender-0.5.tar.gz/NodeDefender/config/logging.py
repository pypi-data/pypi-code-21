import NodeDefender

def enabled():
    return True if NodeDefender.config.parser['LOGGING']['ENABLED'] == 'True' else False

def level():
    return NodeDefender.config.parser['LOGGING']['LEVEL']

def type():
    return NodeDefender.config.parser['LOGGING']['TYPE']

def name():
    return NodeDefender.config.parser['LOGGING']['FILEPATH']

def server():
    return NodeDefender.config.parser['LOGGING']['SERVER']

def port():
    return NodeDefender.config.parser['LOGGING']['PORT']

def get_cfg(key):
    return NodeDefender.config.parser['LOGGING'][key]

def set_cfg(**kwargs):
    for key, value in kwargs.items():
        NodeDefender.config.parser['LOGGING'][key] = str(value)

    return NodeDefender.config.write()
