from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class NewsletterConfig(AppConfig):
    name = 'cms_qe_newsletter'
    verbose_name = _('CMS QE Newsletter')
