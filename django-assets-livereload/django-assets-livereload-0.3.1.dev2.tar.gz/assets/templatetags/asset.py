from django import template
from django.utils.safestring import mark_safe
from django.contrib.staticfiles.templatetags.staticfiles import static

# If we have jinja2 templates
try:
    from django_jinja import library
except:
    class library:
        global_function = lambda x: x
        filter = lambda x: x

from ..manifest import Manifest

register = template.Library()


@register.simple_tag
@library.global_function
def asset(bundle_id):
    return mark_safe(Manifest.find(bundle_id))
