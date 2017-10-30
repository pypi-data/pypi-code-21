import os
from collections import OrderedDict

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import six
from django.apps import apps
from django.contrib.staticfiles import finders

from .storage import ManifestStorage


class ManifestAppDirsFinder(finders.AppDirectoriesFinder):
    storage_class = ManifestStorage

    def __init__(self, app_names=None, *args, **kwargs):
        # The list of apps that are handled
        self.apps = []
        # Mapping of app names to storage instances
        self.storages = OrderedDict()
        app_configs = apps.get_app_configs()
        if app_names:
            app_names = set(app_names)
            app_configs = [ac for ac in app_configs if ac.name in app_names]
        for app_config in app_configs:
            app_storage = self.storage_class(
                os.path.join(app_config.path, self.source_dir), app_name=app_config.name)
            if os.path.isdir(app_storage.location):
                self.storages[app_config.name] = app_storage
                if app_config.name not in self.apps:
                    self.apps.append(app_config.name)


class ManifestFinder(finders.FileSystemFinder):
    def __init__(self, app_names=None, *args, **kwargs):
        # List of locations with static files
        self.locations = []
        # Maps dir paths to an appropriate storage instance
        self.storages = OrderedDict()
        if not isinstance(settings.STATICFILES_DIRS, (list, tuple)):
            raise ImproperlyConfigured(
                "Your STATICFILES_DIRS setting is not a tuple or list; "
                "perhaps you forgot a trailing comma?")
        for root in settings.STATICFILES_DIRS:
            if isinstance(root, (list, tuple)):
                prefix, root = root
            else:
                prefix = ''
            if settings.STATIC_ROOT and os.path.abspath(settings.STATIC_ROOT) == os.path.abspath(root):
                raise ImproperlyConfigured(
                    "The STATICFILES_DIRS setting should "
                    "not contain the STATIC_ROOT setting")
            if (prefix, root) not in self.locations:
                self.locations.append((prefix, root))
        for prefix, root in self.locations:
            filesystem_storage = ManifestStorage(location=root)
            filesystem_storage.prefix = prefix
            self.storages[root] = filesystem_storage

