from shuup.apps import AppConfig as ShuupAppConfig


class AppConfig(ShuupAppConfig):
    name = 'scatl.tests.testproject.theme'
    label = 'scatl.tests.testproject.theme'
    provides = {
        'xtheme': 'scatl.tests.testproject.theme.xtheme:Xtheme',
        'front_urls': ['scatl.tests.testproject.theme.urls:urlpatterns'],
    }
