from django import template
from django.conf import settings
import importlib

register = template.Library()


@register.simple_tag
def get_menu_items():
    apps = settings.JCMS_APPS
    items = []
    for app in apps:
        try:
            imported = importlib.import_module(app + '.jcms.menu_item').MenuItem
            items.append(imported)
        except ImportError:
            print('Import for this app is not found!')
            raise

    return items
