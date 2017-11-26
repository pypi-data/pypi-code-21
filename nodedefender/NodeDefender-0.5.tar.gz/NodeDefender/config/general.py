from datetime import datetime
import NodeDefender

def hostname():
    return os.uname().nodename

def uptime():
    return str(datetime.now() - _loaded_at)

def run_mode():
    return NodeDefender.config.parser['GENERAL']['run_mode']

def secret_key():
    return NodeDefender.config.parser['GENERAL']['KEY']

def secret_salt():
    return NodeDefender.config.parser['GENERAL']['SALT']

def server_name():
    return NodeDefender.config.parser['GENERAL']['SERVERNAME']

def server_port():
    return NodeDefender.config.parser['GENERAL']['PORT']

def self_registration():
    return eval(NodeDefender.config.parser['GENERAL']['SELF_REGISTRATION'])

def get_cfg(key):
    return NodeDefender.config.parser['GENERAL'][key]

def set_cfg(**kwargs):
    for key, value in kwargs.items():
        NodeDefender.config.parser['GENERAL'][key] = str(value)

    return NodeDefender.config.write()
