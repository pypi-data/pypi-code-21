from collections import OrderedDict

from django import template
from django.utils import six

import nexus
from nexus.conf import nexus_settings
from nexus.modules import NexusModule

register = template.Library()


@register.simple_tag
def nexus_media_prefix():
    return nexus_settings.MEDIA_PREFIX.rstrip('/')


@register.simple_tag
def nexus_version():
    return nexus.__version__


@register.inclusion_tag('nexus/navigation.html', takes_context=True)
def show_navigation(context):
    site = context.get('nexus_site', NexusModule.get_global('site'))
    request = context['request']

    category_link_set = OrderedDict([(k, {
        'label': v,
        'links': [],
    }) for k, v in site.get_categories()])

    for namespace, module in six.iteritems(site._registry):
        module, category = module

        if module.permission and not request.user.has_perm(module.permission):
            continue

        home_url = module.get_home_url(context['request'])

        if not home_url:
            continue

        active = request.path.startswith(home_url)

        if category not in category_link_set:
            if category:
                label = site.get_category_label(category)
            else:
                label = None
            category_link_set[category] = {
                'label': label,
                'links': []
            }

        category_link_set[category]['links'].append((module.get_title(), home_url, active))
        category_link_set[category]['active'] = active

    return {
        'nexus_site': site,
        'category_link_set': six.itervalues(category_link_set),
    }
