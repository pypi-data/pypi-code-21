import rediscluster


class StrictRedisCluster(rediscluster.StrictRedisCluster):
    def __init__(self, host, port):
        super().__init__(host=host, port=port, decode_responses=True)
