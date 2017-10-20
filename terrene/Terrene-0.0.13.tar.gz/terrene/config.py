"""
Configures the SDK
"""
import os


class URL:
    def __init__(self, protocol: str, host: str, port: int):
        self.protocol, self.host, self.port = protocol, host, port

    def __call__(self, *args, **kwargs):
        return '{}://{}:{}'.format(self.protocol, self.host, self.port)

api = URL(
    os.environ.get('API_PROTOCOL', 'https'),
    os.environ.get('API_HOST', 'api.terrene.co'),
    os.environ.get('API_PORT', 443))
portal = URL(
    os.environ.get('PORTAL_PROTOCOL', 'https'),
    os.environ.get('PORTAL_HOST', 'portal.terrene.co'),
    os.environ.get('PORTAL_PORT', 443))
