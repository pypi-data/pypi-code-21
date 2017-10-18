from collections import OrderedDict

import django
from django import template

from allauth import app_settings as allauth_settings
from allauth.socialaccount.templatetags import socialaccount as tt_social


register = template.Library()

if django.VERSION >= (1, 9):
    simple_tag = register.simple_tag
else:
    simple_tag = register.assignment_tag


@simple_tag
def is_socialaccount_enabled():
    return allauth_settings.SOCIALACCOUNT_ENABLED and tt_social.get_providers()


@simple_tag
def get_accounts_by_providers(user):
    providers = tt_social.get_providers()
    accounts = tt_social.get_social_accounts(user)

    providers_with_accounts = OrderedDict(
        (provider, accounts.get(provider.id, []))
        for provider in providers
    )

    return providers_with_accounts
