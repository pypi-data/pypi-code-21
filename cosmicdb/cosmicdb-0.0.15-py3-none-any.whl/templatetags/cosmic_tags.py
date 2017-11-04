from django.conf import settings
from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def get_site_title():
    return settings.COSMICDB_SITE_TITLE or "CosmicDB"

@register.simple_tag
def get_signup_link_login():
    if hasattr(settings, 'COSMICDB_ALLOW_SIGNUP'):
        if settings.COSMICDB_ALLOW_SIGNUP or False:
            return mark_safe('<a href="%s">Sign up</a>' % reverse('signup'))
    return ''

