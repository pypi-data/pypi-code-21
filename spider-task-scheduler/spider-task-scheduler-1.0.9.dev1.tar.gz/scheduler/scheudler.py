from rediscluster import StrictRedisCluster


class RedisTaskScheduler:
    def __init__(self, nodes=[{"host": "172.16.8.147", "port": "6379"}]):
        self.redis = StrictRedisCluster(startup_nodes=nodes, decode_responses=True)

    def push(self, name, task):
        print "push task:" + task
        self.redis.lpush(name, task)

    def pop(self, name):
        return self.redis.rpop(name)


if __name__ == "__main__":
    print ""
