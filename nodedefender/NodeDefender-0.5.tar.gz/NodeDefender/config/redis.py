import NodeDefender

def enabled():
    return True if NodeDefender.config.parser['REDIS']['ENABLED'] == 'True' else False

def host():
    return NodeDefender.config.parser['REDIS']['HOST']

def port():
    return NodeDefender.config.parser['REDIS']['PORT']

def database():
    return NodeDefender.config.parser['REDIS']['DATABASE']

def get_cfg(key):
    return NodeDefender.config.parser['REDIS'][key.upper()]

def set_cfg(**kwargs):
    for key, value in kwargs.items():
        NodeDefender.config.parser['REDIS'][key] = str(value)

    return NodeDefender.config.write()
