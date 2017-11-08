from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase

from .models import Icon


class IconPlugin(CMSPluginBase):
    model = Icon
    name = _('Icon')
    module = _('Generic')
    render_template = 'cmsplugin_ss_icon/icon.html'
    allow_children = False


plugin_pool.register_plugin(IconPlugin)
