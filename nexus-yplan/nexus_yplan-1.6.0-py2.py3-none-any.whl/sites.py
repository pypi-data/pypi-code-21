# Core site concept heavily inspired by django.contrib.sites
import mimetypes
import os
import posixpath
import stat
from collections import OrderedDict
from functools import update_wrapper, wraps

from django.conf.urls import url
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse, HttpResponseNotModified, HttpResponseRedirect
from django.utils import six
from django.utils.http import http_date
from django.utils.six.moves import urllib
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.static import was_modified_since

from nexus.compat import context_processors, render, render_to_string, reverse, subinclude, user_is_authenticated
from nexus.conf import nexus_settings

NEXUS_ROOT = os.path.normpath(os.path.dirname(__file__))


class NexusSite(object):
    def __init__(self, name=None, app_name='nexus'):
        self._registry = {}
        self._categories = OrderedDict()
        if name is None:
            self.name = 'nexus'
        else:
            self.name = name
        self.app_name = app_name

    def register_category(self, category, label, index=None):
        if index:
            self._categories.insert(index, category, label)
        else:
            self._categories[category] = label

    def register(self, module, namespace=None, category=None):
        module = module(self, category)
        if not namespace:
            namespace = module.get_namespace()
        if namespace:
            module.app_name = module.name = namespace
        self._registry[namespace] = (module, category)
        return module

    def unregister(self, namespace):
        if namespace in self._registry:
            del self._registry[namespace]

    def get_urls(self):
        base_urls = [
            url(r'^media/(?P<module>[^/]+)/(?P<path>.+)$', self.media, name='media'),

            url(r'^$', self.as_view(self.dashboard), name='index'),
        ], self.app_name, self.name

        urlpatterns = [
            url(r'^', subinclude(base_urls)),
        ]
        for namespace, module in self.get_modules():
            urlpatterns += [
                url(r'^%s/' % namespace, subinclude(module.urls)),
            ]

        return urlpatterns

    @property
    def urls(self):
        return self.get_urls()

    def has_permission(self, request, extra_permission=None):
        """
        Returns True if the given HttpRequest has permission to view
        *at least one* page in the admin site.
        """
        permission = request.user.is_active and request.user.is_staff
        if extra_permission:
            permission = permission and request.user.has_perm(extra_permission)
        return permission

    def as_view(self, view, cacheable=False, extra_permission=None):
        """
        Wraps a view in authentication/caching logic

        extra_permission can be used to require an extra permission for this view, such as a module permission
        """
        @wraps(view)
        def inner(request, *args, **kwargs):
            if not user_is_authenticated(request.user):
                return self.login(request)
            elif not self.has_permission(request, extra_permission):
                raise PermissionDenied()
            return view(request, *args, **kwargs)

        # Mark it as never_cache
        if not cacheable:
            inner = never_cache(inner)

        # We add csrf_protect here so this function can be used as a utility
        # function for any view, without having to repeat 'csrf_protect'.
        if not getattr(view, 'csrf_exempt', False):
            inner = csrf_protect(inner)

        inner = ensure_csrf_cookie(inner)

        return update_wrapper(inner, view)

    def get_context(self, request):
        context = context_processors.csrf(request)
        context.update({
            'request': request,
            'nexus_site': self,
            'nexus_media_prefix': nexus_settings.MEDIA_PREFIX.rstrip('/'),
        })
        return context

    def get_modules(self):
        for k, v in six.iteritems(self._registry):
            yield k, v[0]

    def get_module(self, module):
        return self._registry[module][0]

    def get_categories(self):
        for k, v in six.iteritems(self._categories):
            yield k, v

    def get_category_label(self, category):
        return self._categories.get(category, category.title().replace('_', ' '))

    def render_to_string(self, template, context, request, current_app=None):
        if not current_app:
            current_app = self.name
        else:
            current_app = '%s:%s' % (self.name, current_app)

        if request:
            request.current_app = current_app

        context.update(self.get_context(request))

        return render_to_string(template, context=context, request=request)

    def render_to_response(self, template, context, request, current_app=None):
        "Shortcut for rendering to response and default context instances"
        if not current_app:
            current_app = self.name
        else:
            current_app = '%s:%s' % (self.name, current_app)

        if request:
            request.current_app = current_app

        context.update(self.get_context(request))

        return render(request, template, context=context)

    # Our views

    def media(self, request, module, path):
        """
        Serve static files below a given point in the directory structure.
        """
        if module == 'nexus':
            document_root = os.path.join(NEXUS_ROOT, 'media')
        else:
            document_root = self.get_module(module).media_root

        path = posixpath.normpath(urllib.parse.unquote(path))
        path = path.lstrip('/')
        newpath = ''
        for part in path.split('/'):
            if not part:
                # Strip empty path components.
                continue
            drive, part = os.path.splitdrive(part)
            head, part = os.path.split(part)
            if part in (os.curdir, os.pardir):
                # Strip '.' and '..' in path.
                continue
            newpath = os.path.join(newpath, part).replace('\\', '/')
        if newpath and path != newpath:
            return HttpResponseRedirect(newpath)
        fullpath = os.path.join(document_root, newpath)
        if os.path.isdir(fullpath):
            raise Http404("Directory indexes are not allowed here.")
        if not os.path.exists(fullpath):
            raise Http404('"%s" does not exist' % fullpath)
        # Respect the If-Modified-Since header.
        statobj = os.stat(fullpath)
        mimetype = mimetypes.guess_type(fullpath)[0] or 'application/octet-stream'
        if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                                  statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
            return HttpResponseNotModified(content_type=mimetype)
        contents = open(fullpath, 'rb').read()
        response = HttpResponse(contents, content_type=mimetype)
        response["Last-Modified"] = http_date(statobj[stat.ST_MTIME])
        response["Content-Length"] = len(contents)
        return response

    @never_cache
    def login(self, request, form_class=None):
        "Login form"
        if user_is_authenticated(request.user):
            return HttpResponseRedirect(reverse('nexus:index', current_app=self.name))

        return HttpResponseRedirect(
            '{login}?{get}'.format(
                login=reverse('admin:login'),
                get=urllib.parse.urlencode({REDIRECT_FIELD_NAME: request.path})
            )
        )

    def dashboard(self, request):
        "Basic dashboard panel"
        module_set = []
        for namespace, module in self.get_modules():
            home_url = module.get_home_url(request)

            if hasattr(module, 'render_on_dashboard'):
                # Show by default, unless a permission is required
                if not module.permission or request.user.has_perm(module.permission):
                    module_set.append((module.get_dashboard_title(), module.render_on_dashboard(request), home_url))

        return self.render_to_response('nexus/dashboard.html', {
            'module_set': module_set,
        }, request)


# setup the default site
site = NexusSite()
