
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.views import redirect_to_login
from django.http import Http404, HttpResponsePermanentRedirect
from django.contrib.sites.models import Site

from flatpages.models import FlatPage


DEFAULT_TEMPLATE = 'flatpages/default.html'


def flatpage(request, url):

    if not url.startswith('/'):
        url = '/' + url

    params = {
        'url': url,
        'site_id': settings.SITE_ID
    }

    try:
        f = get_object_or_404(FlatPage, **params)
    except Http404:
        if not url.endswith('/') and settings.APPEND_SLASH:
            url += '/'
            f = get_object_or_404(FlatPage, **params)
            return HttpResponsePermanentRedirect('%s/' % request.path)
        else:
            raise

    if f.registration_required and not request.user.is_authenticated():
        return redirect_to_login(request.path)

    template_name = f.template_name or DEFAULT_TEMPLATE

    return render(request, template_name, {'flatpage': f})
