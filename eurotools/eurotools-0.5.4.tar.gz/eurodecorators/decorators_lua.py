class StoneMRL(object):
    '''
        Method Rate limiter.
        Args:
            param1 (redis object): Redis connection
    '''
    def __init__(self, redis_con):
        self.redis_con = redis_con

    def callRL(self, key, subkey, ex_num, limit_time, now):
        '''
            Register the lua script if it did not. And return the result of execute it.
            Args:
                param1(string): key to limit.
                param2(string): this is the name and score of set.
                param3(int): the number of executions at the same time
                param4(int): windows size
                param4(int): epoch
            Returns:
                int: 0 or 1. if returns 1 the method has to wait, when returns 0 the methos continues.
        '''
        if not hasattr(self.redis_con, 'method_rate_limiter'):
            self.redis_con.method_rate_limiter = self.redis_con.register_script(self._getLua())

        return self.redis_con.method_rate_limiter(keys=[ex_num, limit_time, now], args=[key, subkey])

    def _getLua(self):
        '''
            Return the lua script.
        '''
        return '''
            -- create vars
            local key = ARGV[1]
            local subkey = ARGV[2]
            local limit = tonumber(KEYS[1])
            local limit_time = tonumber(KEYS[2])
            local now = tonumber(KEYS[3])
            local reject = 1
            local stat1 = -1
            local total = 0

            --maintenance
            redis.call('ZREMRANGEBYSCORE', key, '-inf', now-limit_time)

            --check
            stat1 = redis.call('ZRANK', key, subkey)
            if stat1 then
                if stat1 < limit then
                    reject = 0
                else
                    reject = 1
                end
                return reject
            end

            --add
            total = redis.call('ZCARD', key)
            if total < limit then
                reject = 0
            else
                reject = 1
            end
            redis.call('ZADD', key, subkey, subkey)
            return reject
        '''
