from django.conf import settings


class Settings(object):
    """
    Shadow Django's settings with a little logic
    """
    @property
    def MEDIA_PREFIX(self):
        prefix = getattr(settings, 'NEXUS_MEDIA_PREFIX', '/nexus/media/')
        if getattr(settings, 'NEXUS_USE_DJANGO_MEDIA_URL', False):
            prefix = getattr(settings, 'MEDIA_URL', prefix)
        return prefix


nexus_settings = Settings()
