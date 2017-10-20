# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FilerVideoConfig(AppConfig):
    name = 'ripiu.cmsplugin_filer_video'
    verbose_name = _('Self hosted videos')
