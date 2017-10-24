from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def hijack_notification_proxy(context):
    """
    This tag only renders hijack_notification if the library is present
    """
    if hasattr(settings, 'IMPERSONATION_APPS'):
        from hijack.templatetags.hijack_tags import hijack_notification
        return hijack_notification(context)

    return ''
