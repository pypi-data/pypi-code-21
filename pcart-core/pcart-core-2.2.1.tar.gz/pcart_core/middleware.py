from django.contrib.sites.shortcuts import get_current_site
from django.middleware.common import CommonMiddleware
from django import http
from .models import RootFile


class PCartCommonMiddleware(CommonMiddleware):
    response_redirect_class = http.HttpResponseRedirect


class RootFileRouterMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def _get_root_file_instance(self, site, path):
        from django.core.cache import cache
        cache_key = 'rootfiles-list-%s' % site.id
        root_files_route = cache.get(cache_key)
        if root_files_route is None:
            root_files_route = {
                '/%s' % k: v
                for k, v in RootFile.objects.filter(site=site, published=True).values_list('file_name', 'id')}
            cache.set(cache_key, root_files_route, 3600)
        _id = root_files_route.get(path)
        if _id is not None:
            try:
                result = RootFile.objects.get(pk=_id)
                return result
            except RootFile.DoesNotExist:
                pass

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        site = get_current_site(request)
        root_file = self._get_root_file_instance(site, request.get_full_path())
        if root_file is not None:
            response = root_file.view(request)
            return response

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
