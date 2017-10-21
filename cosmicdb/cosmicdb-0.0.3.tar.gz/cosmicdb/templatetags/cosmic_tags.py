from django.conf import settings
from django import template

register = template.Library()


@register.simple_tag
def get_site_title():
    return settings.COSMICDB_SITE_TITLE or "CosmicDB"
