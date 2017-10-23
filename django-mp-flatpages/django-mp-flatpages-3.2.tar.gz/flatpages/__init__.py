
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FlatPagesConfig(AppConfig):
    name = 'flatpages'
    verbose_name = _("Flat Pages")


default_app_config = 'flatpages.FlatPagesConfig'

__version__ = '3.2'
