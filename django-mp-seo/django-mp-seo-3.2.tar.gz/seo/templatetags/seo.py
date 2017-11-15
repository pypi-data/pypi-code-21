
from django.template import Library

from ..lib import get_page_meta


register = Library()


@register.simple_tag(takes_context=True, name='get_page_meta')
def get_page_meta_tag(context):
    return get_page_meta(context.request, context)
