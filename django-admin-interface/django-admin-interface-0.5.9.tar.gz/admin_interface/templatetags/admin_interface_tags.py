# -*- coding: utf-8 -*-

from django import template
# from django.core.cache import cache

from admin_interface.models import Theme
from admin_interface.version import __version__

register = template.Library()

try:
    assignment_tag = register.assignment_tag
except AttributeError:
    assignment_tag = register.simple_tag


@assignment_tag(takes_context=True)
def get_admin_interface_theme(context):

    # return cache.get_or_set(
    #     'admin_interface_theme', Theme.get_active_theme, 1)

    theme = None
    request = context.get('request', None)

    if request:
        theme = getattr(request, 'admin_interface_theme', None)

    if not theme:
        theme = Theme.get_active_theme()

    if request:
        request.admin_interface_theme = theme

    return theme


@assignment_tag(takes_context=False)
def get_admin_interface_version():
    return __version__
