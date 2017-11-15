from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class OrfiumOAuth2Account(ProviderAccount):

    pass


class OrfiumOAuth2Provider(OAuth2Provider):
    id = 'orfium_oauth2'
    # Name is displayed to ordinary users -- don't include protocol
    name = 'Orfium'
    account_class = OrfiumOAuth2Account

    def extract_uid(self, data):
        return str(data['username'])

    def get_profile_fields(self):
        return [
            'username',
            'first_name',
            'last_name',
            'avatar',
            'email',
            'verified',
        ]

    def get_default_scope(self):
        return ['read', 'write']

    def extract_common_fields(self, data):
        return {
            'username': data.get('username'),
            'email':data.get('email'),
            'first_name': data.get('first_name', ''),
            'last_name': data.get('last_name', ''),
        }


provider_classes = [OrfiumOAuth2Provider]
