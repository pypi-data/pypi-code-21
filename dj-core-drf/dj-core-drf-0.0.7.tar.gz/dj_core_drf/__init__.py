from pkg_resources import get_distribution


__version__ = get_distribution('dj_core_drf').version

default_app_config = 'dj_core_drf.apps.DjCoreDRFConfig'
