"""
Sentry Client
"""
from raven import Client


class SentryClient:
    """
    SentryClient Wrapper
    """
    def __init__(self, sentry_id, mode)-> None:
        if mode == 'production' and not sentry_id:
            self._client = Client(sentry_id)
        else:
            self._client = Client()

    def get_sentry_client(self):
        """
        Get sentry client
        :return:
        """
        return self._client


def get_sentry_client(sentry_id='', mode='production'):
    """
    Get sentry client from config
    :return:
    """
    return SentryClient(sentry_id, mode).get_sentry_client()
