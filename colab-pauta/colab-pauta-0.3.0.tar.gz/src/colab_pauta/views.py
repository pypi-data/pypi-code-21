from django.conf import settings
from colab.plugins.views import ColabProxyView


class ColabPautaProxyView(ColabProxyView):
    app_label = 'colab_pauta'
    diazo_theme_template = 'proxy/pauta.html'
    rewrite = (
        (r'^/pautas/admin/login/?$', settings.LOGIN_URL),
        (r'^/pautas/admin/login/(.*)$', r'{}\1'.format(settings.LOGIN_URL)),
        (r'^/pautas/admin/logout/?$', r'/account/logout'),
        (r'^/pautas/admin/logout/(.*)$', r'{}\1'.format('/account/logout')),
    )

    def get_proxy_request_headers(self, request):
        headers = super(ColabPautaProxyView,
                        self).get_proxy_request_headers(request)

        if request.user.is_authenticated():
            headers["Auth-user"] = request.user.username

        return headers
