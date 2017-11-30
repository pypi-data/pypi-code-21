import dill


def dill_serialize(self, value):
    """ patch serialize
        Using python dill library to support
        class instances serialization
    """
    return dill.dumps(value)

def monkey_patch():
    try:
        from redis_cache.serializers import PickleSerializer as ps
    except ImportError:
        return

    ps.serialize = dill_serialize

