class RedisConfig(object):
    def __init__(self, host, port, db=0):
        self.host = host
        self.port = port
        self.db = db
