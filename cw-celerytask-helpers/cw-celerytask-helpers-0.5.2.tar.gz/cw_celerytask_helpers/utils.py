import celery
import redis
from redis.client import Redis

def get_redis_client():
    conf = celery.current_app.conf
    url = conf.get('CUBICWEB_CELERYTASK_REDIS_URL')
    BROKER_TRANSPORT_OPTIONS = conf.get('BROKER_TRANSPORT_OPTIONS')
    if url.startswith('redis-sentinel://') and 'sentinels' in BROKER_TRANSPORT_OPTIONS:
        from redis.sentinel import Sentinel
        service_name = BROKER_TRANSPORT_OPTIONS.get('service_name', 'master')
        return Sentinel(BROKER_TRANSPORT_OPTIONS['sentinels'],
                        socket_timeout=0.1).master_for(service_name,
                                                       redis_class=Redis,
                                                       socket_timeout=0.1)
    elif url:
        return redis.Redis.from_url(url)
