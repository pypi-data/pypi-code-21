from django.conf import settings
from colab.plugins.views import ColabProxyView


class ColabAudienciasPluginProxyView(ColabProxyView):
    app_label = 'colab_audiencias'
    diazo_theme_template = 'proxy/audiencias.html'
    rewrite = (
        (r'^/audiencias/login/?$', r'{}'.format(settings.LOGIN_URL)),
    )

    def get_proxy_request_headers(self, request):
        headers = super(ColabAudienciasPluginProxyView,
                        self).get_proxy_request_headers(request)

        if request.user.is_authenticated():
            headers["Auth-user"] = request.user.username

        return headers
