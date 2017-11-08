import django.core.cache


def put(key, value, timeout=None):
    django.core.cache.cache.set(key, value, timeout)


def get(key):
    return django.core.cache.cache.get(key)


def get_or_put(key, fun_getvalue, timeout=None):
    value = get(key)
    if not value:
        value = fun_getvalue()
        put(key, value, timeout)
    return value


def delete(key):
    django.core.cache.cache.delete(key)


def clear():
    django.core.cache.cache.clear()
