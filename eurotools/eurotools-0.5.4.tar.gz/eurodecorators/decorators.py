import os
import time
from . import decorators_lua
import logging
logger = logging.getLogger('eurotools')


class TimeOutException(Exception):
    pass


def max_sim_execs():
    '''
        Decorator to limit concurrents executions of the same method.
        Args:
            param1(string): key to limit.
            param2(int): maximun number of concurrents executions.
            param3(redis): redis instance.
            param4(int): windows size in seconds. (optional)
        Returns:
            int: 0 or 1. if returns 1 the method has to wait, when returns 0 the methos continues.
    '''
    '''
    Example:
        @max_sim_execs('estemetodo', 2, r)
    '''
    def p_decorate(func):
        def func_wrapper(*args, **kwargs):
            def check_set_size(redis, limit, key):
                if redis:
                    items = redis.zcard(key)
                    if items >= limit:
                        logger.warning('Rate limiter is full')

            try:
                key, limit, redis, limit_time = args[0]._get_decorator_params()
            except:
                key = kwargs.pop('key', 'MAX_SIM_EXEC')
                limit = kwargs.pop('limit', 0)
                redis = kwargs.pop('redis', None)
                limit_time = kwargs.pop('limit_time', 300)
            limit_time *= 1000000
            result = False
            check_set_size(redis, limit, key)
            if redis and limit > 0:
                srl = decorators_lua.StoneMRL(redis)
                reject = 1
                first_time = True
                lock = redis.wait_for_reset_lock(key, locktime=limit_time)
                subkey = '{0}.{1}'.format(int(time.time() * 1000000), str(os.getpid()))
                now = int(time.time() * 1000000)
                bounded_time = now + limit_time
                while reject and (now < bounded_time):
                    reject = srl.callRL(key, subkey, limit, limit_time, now)
                    if first_time:
                        redis.reset_lock(lock)
                        first_time = False
                    if reject:
                        time.sleep(0.01)
                        now = int(time.time() * 1000000)
                if reject == 0:
                    result = func(*args, **kwargs)
                else:
                    redis.zrem(key, subkey)
                    raise TimeOutException
                redis.zrem(key, subkey)
            else:
                result = func(*args, **kwargs)
            return result
        return func_wrapper
    return p_decorate
