# -*- encoding:utf-8 -*-
from .add_ons import get_addons
from django.conf import settings
from django.contrib.auth.models import Group
from . import settings as local_settings


def get_settings(conf_name):
    if hasattr(settings, conf_name):
        return {conf_name: getattr(settings, conf_name)}
    if hasattr(local_settings, conf_name):
        return {conf_name: getattr(local_settings, conf_name)}
    return {}


def context(request):
    user = request.user
    if user.is_superuser:
        groups = Group.objects.all().values_list('name', flat=True)
    else:
        groups = user.groups.all().values_list('name', flat=True)
    app_context = {'addons': get_addons().values()}
    app_context.update({'groups': groups})
    app_context.update(get_settings('APP_NAME'))
    app_context.update(get_settings('AUTHOR'))
    app_context.update(get_settings('CAN_SIGNUP'))
    app_context.update(get_settings('CAN_RESET_PASSWORD'))
    app_context.update({'SIDEBAR_COLLAPSED': request.session.get('sidebar_collapsed', 'false')})
    return app_context
