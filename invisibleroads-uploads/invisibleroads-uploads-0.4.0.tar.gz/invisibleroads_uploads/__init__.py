from invisibleroads_macros.configuration import set_default
from invisibleroads_posts import add_website_dependency

from .views import add_routes


def includeme(config):
    configure_settings(config)
    configure_assets(config)
    add_routes(config)


def configure_settings(config):
    settings = config.registry.settings
    set_default(settings, 'upload.id.length', 32, int)
    add_website_dependency(config)


def configure_assets(config):
    config.add_cached_static_view(
        '_/invisibleroads-uploads', 'invisibleroads-uploads:assets')
