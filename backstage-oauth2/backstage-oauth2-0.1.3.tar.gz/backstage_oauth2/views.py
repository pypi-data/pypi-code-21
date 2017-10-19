# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse
from allaccess.views import OAuthCallback, OAuthRedirect
from allaccess.compat import get_user_model

from backstage_oauth2.client import OAuth2BearerClient


class BackstageOAuthCallback(OAuthCallback):

    info_lookup_field = 'email'
    client_class = OAuth2BearerClient
    reverse_error_redirect = 'admin:index'
    reverse_login_redirect = 'admin:index'

    def get_error_redirect(self, provider, reason):
        return reverse(self.reverse_error_redirect)

    def get_login_redirect(self, provider, user, access, new=False):
        return reverse(self.reverse_login_redirect)

    def get_client(self, provider):
        return self.client_class(provider)

    def get_user_id(self, provider, info):
        identifier = None
        if hasattr(info, 'get'):
            identifier = info.get(self.info_lookup_field)

        if identifier is not None:
            return identifier

        return super(BackstageOAuthCallback, self).get_user_id(provider, info)

    def get_or_create_user(self, provider, access, info):
        email = info.get('email', '')
        username = info.get('username', email)
        if username:
            User = get_user_model()
            try:
                return User.objects.get(username=username, email=email)
            except User.DoesNotExist:
                pass
            username = username
            kwargs = {
                User.USERNAME_FIELD: username,
                'email': info.get('email', ''),
                'password': None,
                'first_name': info.get('name', ''),
                'last_name': info.get('surname', ''),
            }
            return User.objects.create_user(**kwargs)

        return super(BackstageOAuthCallback, self).get_or_create_user(provider, access, info)


class BackstageOAuthRedirect(OAuthRedirect):
    provider = ''

    def get_redirect_url(self, **kwargs):
        return super(BackstageOAuthRedirect, self).get_redirect_url(provider=self.provider)
