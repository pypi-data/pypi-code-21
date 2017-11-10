# -*- coding: utf-8 -*-

from django.apps import AppConfig
# from django.db.utils import OperationalError


class NavsyConfig(AppConfig):

    name = 'navsy'
    verbose_name = 'Navigation'

    def ready(self):

        from navsy import cache, settings, signals

        settings.check_settings()
        cache.delete_data()

        # try:
        #     signals.post_migrate_app(self)
        #     cache.delete_data()
        #
        # except OperationalError:
        #     pass
