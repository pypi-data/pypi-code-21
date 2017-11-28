import redis
from aalam_common.config import cfg


def baseapp_redisify_name(name):
    return "__common__:%s" % name


def get_redis_obj():
    if not getattr(cfg.CONF, 'redis', None) or \
            not getattr(cfg.CONF.redis, 'url', None):
        return
    return redis.StrictRedis.from_url(cfg.CONF.redis.url)


redis_conn = get_redis_obj()


def redis_bgsave():
    if redis_conn.info().get('rdb_bgsave_in_progress'):
        return

    try:
        redis_conn.bgsave()
    except:
        pass
