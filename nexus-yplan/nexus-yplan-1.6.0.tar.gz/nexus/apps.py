from django.apps import AppConfig


class NexusAppConfig(AppConfig):
    name = 'nexus'
    verbose_name = "Nexus"

    def ready(self):
        from nexus.checks import register_checks
        register_checks()

        self.module.autodiscover()
