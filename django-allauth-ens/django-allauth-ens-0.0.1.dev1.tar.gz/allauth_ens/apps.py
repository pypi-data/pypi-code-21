from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ENSAllauthAppConfig(AppConfig):
    name = 'allauth_ens'
    verbose_name = _("ENS Authentication")
