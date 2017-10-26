import tldextract
from urllib.parse import urlparse


class Url:
    domain = None
    parsed_url = None
    url = None
    scheme = None
    origin_url = None
    provider = None
    provider_name = None
    provider_url = None

    def __init__(self, url, origin_url=None):
        self.url = url.strip('\'')
        self.origin_url = origin_url.strip('\'') if origin_url.strip('\'') is not None else self.url
        self.domain = tldextract.extract(self.origin_url)
        self.parsed_url = urlparse(self.origin_url)

    def is_valid(self):
        if self.get_scheme() in ['http', 'https']:
            return True

        return False

    def get_scheme(self):
        return self.parsed_url.scheme

    def get_url(self):
        return self.url

    def get_origin_url(self):
        return self.origin_url

    def get_provider(self):
        return '.'.join(part for part in [self.domain.domain, self.domain.suffix] if part)

    def get_provider_name(self):
        return self.domain.domain

    def get_provider_url(self):
        return self.get_scheme() + '://' + '.'.join(part for part in self.domain if part)

    def get_properties(self):
        return {
            "scheme": self.get_scheme(),
            "url": self.get_url(),
            "origin_url": self.get_origin_url(),
            "provider": self.get_provider(),
            "provider_name": self.get_provider_name(),
            "provider_url": self.get_provider_url()
        }
