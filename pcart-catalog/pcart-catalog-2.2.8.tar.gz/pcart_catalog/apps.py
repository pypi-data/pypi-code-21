from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PCartCatalogConfig(AppConfig):
    name = 'pcart_catalog'
    verbose_name = _('Catalog')
