# -*- coding: utf-8 -*-
from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount

from allauth_cas.providers import CASProvider


class ClipperAccount(ProviderAccount):
    pass


class ClipperProvider(CASProvider):
    id = 'clipper'
    name = 'Clipper'
    account_class = ClipperAccount

    def extract_email(self, data):
        username, _, _ = data
        return '{}@clipper.ens.fr'.format(username)

    def extract_common_fields(self, data):
        common = super(ClipperProvider, self).extract_common_fields(data)
        common['email'] = self.extract_email(data)
        return common

    def extract_email_addresses(self, data):
        email = self.extract_email(data)
        return [
            EmailAddress(
                email=email,
                verified=True,
                primary=True,
            )
        ]

    def extract_extra_data(self, data):
        extra = super(ClipperProvider, self).extract_extra_data(data)
        extra['username'] = data[0]
        extra['email'] = self.extract_email(data)
        return extra


provider_classes = [ClipperProvider]
