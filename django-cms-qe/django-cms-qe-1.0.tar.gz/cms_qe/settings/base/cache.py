"""
Caching setting by default in-memory without need to configure anything.
"""

# Caching
# https://docs.djangoproject.com/en/1.11/topics/cache/

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
