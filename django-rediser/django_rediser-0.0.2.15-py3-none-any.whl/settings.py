import threading

try:
    from django.conf import settings
except ImportError:
    settings = object()


class RediserSettings(dict):
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = super().__new__(cls)
        return cls.__singleton_instance

    def __init__(self):
        super().__init__()
        _django_rediser_settings = getattr(settings, 'DJANGO_REDISER', {})
        self.update({
            'REDIS_HOST': _django_rediser_settings.get('REDIS_HOST', 'localhost'),
            'REDIS_PORT': _django_rediser_settings.get('REDIS_PORT', 6379),
            'REDIS_DB': _django_rediser_settings.get('REDIS_DB', 0),
        })


rediser_settings = RediserSettings()
