from django.conf import settings


class Settings(object):
    MODE_TEST = 1
    MODE_LIVE = 2
    
    @property
    def mode(self):
        return getattr(settings, 'STRIPE_MODE', self.MODE_TEST)

    @property
    def is_live(self):
        return self.mode is self.MODE_LIVE

    @property
    def api_key(self):
        test_api_key = getattr(settings, 'STRIPE_TEST_API_KEY', None)
        api_key = getattr(settings, 'STRIPE_API_KEY', None)

        return api_key if self.is_live else test_api_key
