# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

try:
    from importlib import import_module
except ImportError:
    # Python 2.6 fallback
    from django.utils.importlib import import_module

from django.conf import settings
from django.conf.urls import include, url

_cache = {}


class BaseAddon(object):

    """Add-ons should inherit from this"""
    # Must fill in!
    slug = None
    # fontawesome 3.2.1 icon class name
    iconclass = 'fa fa-circle-blank'
    # General urlpatterns that will reside in /background/addon-slug/...
    urlpatterns = []
    navs = {
        # Like this: _('Users'): {"url_name":"wxrbot:user_list", "iconclass": "fa fa-user", "nav_id":"nav-user"},
    }
    sort_id = 0

    class RenderMedia:
        js = []
        css = {}


def register(AddonsClass):
    """
    Register a add-on class. This function will call back your add-on's
    constructor.
    """
    if AddonsClass in list(_cache.keys()):
        raise Exception("Addons class already registered")
    addon = AddonsClass()
    _cache[AddonsClass] = addon


def get_addons():
    """Get loaded addons - do not call before all addons are loaded."""
    return _cache


def get_addons_urls():
    urlpatterns = []
    for addon in list(get_addons().values()):
        slug = getattr(addon, 'slug', None)
        if slug:
            urlpatterns += [
                url('^' + slug + '/', include(addon.urlpatterns)),
            ]
        else:
            urlpatterns += [
                url('^', include(addon.urlpatterns)),
            ]
    return urlpatterns


def get_module(app, modname, verbose=False, failfast=False, success=True):
    """
    Internal function to load a module from a single app.
    """
    module_name = '%s.%s' % (app, modname)
    try:
        module = import_module(module_name)
    except ImportError as e:
        if failfast:
            if 'No module named' in str(e):
                pass
            else:
                raise e
        elif verbose:
            print("Could not load %r from %r: %s" % (modname, app, e))
        return None
    if success or verbose:
        print("Loaded %r from %r" % (modname, app))
    return module


def load(modname, verbose, failfast, success):
    """
    Loads all modules with name 'modname' from all installed apps.
    If verbose is True, debug information will be printed to stdout.
    If failfast is True, import errors will not be surpressed.
    """
    for app in settings.INSTALLED_APPS:
        get_module(app, modname, verbose, failfast, success)


def load_bgframework_addons(verbose=False, failfast=False, success=True):
    load('bgf_addons', verbose, failfast, success)
