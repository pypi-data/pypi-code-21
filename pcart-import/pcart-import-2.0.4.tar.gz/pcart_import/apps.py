from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PCartImportConfig(AppConfig):
    name = 'pcart_import'
    verbose_name = _('Import')
