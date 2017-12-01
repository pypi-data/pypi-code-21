from . import storage

__all__ = ['get_storage']

def get_storage(storage_name, *args, **kwargs):
    return getattr(storage, "{}Storage".format(storage_name))(*args, **kwargs)

