
from django.middleware.common import MiddlewareMixin
from django.http.response import HttpResponseRedirect


class WWWRedirectMiddleware(MiddlewareMixin):

    def process_request(self, request):
        host = request.get_host()
        if host.lower().startswith('www.'):
            url = request.build_absolute_uri().replace(host, host[4:], 1)
            return HttpResponseRedirect(url)
