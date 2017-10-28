"""
Nexus
~~~~~
"""
from django.utils.module_loading import autodiscover_modules

from nexus.modules import NexusModule
from nexus.sites import NexusSite, site

__version__ = '1.6.0'
VERSION = __version__
__all__ = ('autodiscover', 'NexusSite', 'NexusModule', 'site')

default_app_config = 'nexus.apps.NexusAppConfig'


def autodiscover():
    autodiscover_modules('nexus_modules', register_to=site)
