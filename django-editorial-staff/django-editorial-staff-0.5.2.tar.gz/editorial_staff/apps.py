# Imports from Django.  # NOQA
from django.apps import AppConfig


class EditorialStaffConfig(AppConfig):
    name = 'editorial_staff'
    verbose_name = 'Editorial staff'

    def ready(self):
        pass
