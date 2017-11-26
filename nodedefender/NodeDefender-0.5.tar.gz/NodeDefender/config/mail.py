import NodeDefender

def enabled():
    return True if NodeDefender.config.parser['MAIL']['ENABLED'] == 'True' else False

def server():
    return NodeDefender.config.parser['MAIL']['SERVER']

def port():
    return NodeDefender.config.parser['MAIL']['PORT']

def tls():
    return True if NodeDefender.config.parser['MAIL']['TLS'] == 'True' else False

def ssl():
    return True if NodeDefender.config.parser['MAIL']['SSL'] == 'True' else False

def username():
    return NodeDefender.config.parser['MAIL']['USERNAME']

def password():
    return NodeDefender.config.parser['MAIL']['PASSWORD']

def get_cfg(key):
    return NodeDefender.config.parser['MAIL'][key]

def set_cfg(**kwargs):
    for key, value in kwargs.items():
        NodeDefender.config.parser['MAIL'][key] = str(value)

    return NodeDefender.config.write()
