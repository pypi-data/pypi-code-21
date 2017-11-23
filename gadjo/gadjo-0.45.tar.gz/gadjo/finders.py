# this file derives from django-xstatic:
#   Author: Gautier Hayoun
#   Author-email: ghayoun@gmail.com
#   License: MIT license
#   Home-page: http://github.com/gautier/django-xstatic

import os

from django.conf import settings
from django.contrib.staticfiles import utils
from django.contrib.staticfiles.finders import BaseFinder
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage
try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module


class XStaticStorage(FileSystemStorage):
    """
    A file system storage backend that takes an xstatic package module and works
    for the data contained in it.
    """
    prefix = 'xstatic'

    def __init__(self, package, *args, **kwargs):
        """
        Returns a static file storage if available in the given xstatic package
        """
        try:
            package = import_module(package)
        except ImportError:
            raise ImproperlyConfigured('Cannot import module "%s"' % package)
        location = package.BASE_DIR
        super(XStaticStorage, self).__init__(location, *args, **kwargs)


class XStaticFinder(BaseFinder):
    storage_class = XStaticStorage

    gadjo_deps = ['jquery', 'jquery_ui', 'font_awesome', 'opensans']

    def __init__(self, apps=None, *args, **kwargs):
        # The list of apps that are handled
        self.apps = []
        # Mapping of app module paths to storage instances
        self.storages = {}
        if apps is None:
            apps = settings.INSTALLED_APPS
        apps = list(apps)
        for dep in self.gadjo_deps:
            apps.append('xstatic.pkg.%s' % dep)
        for app in apps:
            if app.lower().startswith('xstatic.'):
                app_storage = self.storage_class(app)
                if os.path.isdir(app_storage.location):
                    self.storages[app] = app_storage
                    if app not in self.apps:
                        self.apps.append(app)
        super(XStaticFinder, self).__init__(*args, **kwargs)

    def find(self, path, all=False):
        """Look for files in the registered xstatic.* packages"""
        if path.startswith(self.storage_class.prefix + '/'):
            path = path[len(self.storage_class.prefix)+1:]
        matches = []
        for app, storage in self.storages.items():
            if storage.exists(path):
                matched_path = storage.path(path)
                if matched_path:
                    if not all:
                        return matched_path
                    matches.append(matched_path)
        return matches

    def list(self, ignore_patterns=[]):
        """List all files in registered xstatic.* packages"""
        for app, storage in self.storages.items():
            for path in utils.get_files(storage, ignore_patterns):
                yield path, storage
