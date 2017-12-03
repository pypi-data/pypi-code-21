from shuup.apps import AppConfig as ShuupAppConfig


class AppConfig(ShuupAppConfig):
    name = 'scatl'
    verbose_name = 'Catalog filters addon'
    label = 'scatl'
    provides = {
        'xtheme_plugin': [
            'scatl.plugins:ScatlPlugin',
        ],
        'api_populator': [
            'scatl.api.api_populator:populate',
        ],
    }
