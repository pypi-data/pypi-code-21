import json

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe

from .. import app_settings

register = template.Library()


@register.filter(is_safe=True)
def js(obj):
    return mark_safe(json.dumps(obj, cls=DjangoJSONEncoder))


@register.inclusion_tag('molo_pwa.html', takes_context=True)
def molo_pwa_meta(context):
    # Pass all PWA_* settings into the template
    pwa_settings = {setting_name: getattr(app_settings, setting_name)
                    for setting_name in dir(app_settings)
                    if setting_name.startswith('PWA_')}
    return {
        'request': context['request'],
        'pwa_settings': pwa_settings
    }
