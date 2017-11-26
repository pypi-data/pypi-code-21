import NodeDefender

def enabled():
    return True if NodeDefender.config.parser['DATABASE']['ENABLED'] == 'True' else False

def engine():
    return NodeDefender.config.parser['DATABASE']['ENGINE']

def username():
    return NodeDefender.config.parser['DATABASE']['USERNAME']

def password():
    return NodeDefender.config.parser['DATABASE']['PASSWORD']

def server():
    return NodeDefender.config.parser['DATABASE']['SERVER']

def port():
    return NodeDefender.config.parser['DATABASE']['PORT']

def db():
    return NodeDefender.config.parser['DATABASE']['DB']

def file():
    return NodeDefender.config.parser['DATABASE']['FILEPATH']

def mysql_uri():
    return 'mysql+pymysql://'+username()+':'+password()+'@'+server()+':'+port()+'/'+db()

def postgresql_uri():
    return 'postgresql://'+username()+':'+password()+'@'\
            +server()+':'+port()+'/'+db()

def sqlite_uri():
    return 'sqlite:///' + NodeDefender.config.parser['DATABASE']['FILEPATH']

def uri():
    db_engine = engine()
    return eval(db_engine + '_uri')()

def get_cfg(key):
    return NodeDefender.config.parser['DATABASE'][key]

def set_cfg(**kwargs):
    for key, value in kwargs.items():
        NodeDefender.config.parser['DATABASE'][key] = str(value)

    return NodeDefender.config.write()
