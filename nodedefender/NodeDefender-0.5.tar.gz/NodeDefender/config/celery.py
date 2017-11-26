import NodeDefender

def enabled():
    return True if NodeDefender.config.parser['CELERY']['ENABLED'] == 'True' else False

def broker():
    return NodeDefender.config.parser['CELERY']['BROKER']

def server():
    return NodeDefender.config.parser['CELERY']['SERVER']

def port():
    return NodeDefender.config.parser['CELERY']['PORT']

def database():
    return NodeDefender.config.parser['CELERY']['DATABASE']

def broker_uri():
    if broker() == 'REDIS':
        return 'redis://'+server()+':'+port()+'/'+database()
    elif broker() == 'AMQP':
        return 'pyamqp://'+server()+':'+port()+'/'+database()
    else:
        return None

def backend_uri():
    if broker() == 'REDIS':
        return 'redis://'+server()+':'+port()+'/'+database()
    elif broker() == 'AMQP':
        return 'rpc://'+server()+':'+port()+'/'+database()
    else:
        return None

def get_cfg(key):
    return NodeDefender.config.parser['CELERY'][key.upper()]

def set_cfg(**kwargs):
    for key, value in kwargs.items():
        NodeDefender.config.parser['CELERY'][key] = str(value)

    return NodeDefender.config.write()
