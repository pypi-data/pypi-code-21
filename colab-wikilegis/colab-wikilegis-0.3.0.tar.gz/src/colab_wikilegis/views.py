from django.conf import settings
from colab.plugins.views import ColabProxyView


class ColabWikilegisPluginProxyView(ColabProxyView):
    app_label = 'colab_wikilegis'
    diazo_theme_template = 'proxy/wikilegis.html'
    rewrite = (
        (r'^/wikilegis/accounts/login/?$', r'{}'.format(settings.LOGIN_URL)),
        (r'^/wikilegis/accounts/register/?$',
            r'{}'.format(settings.LOGIN_URL)),
        (r'^/wikilegis/accounts/password_reset/?$',
            r'{}'.format('/account/password-reset')),
        (r'^/wikilegis/accounts/password_reset/done/?$',
            r'{}'.format('/home')),
        (r'^/wikilegis/accounts/password_change/?$',
            r'{}'.format('/password_change')),
        (r'^/wikilegis/accounts/password_change/done/?$',
            r'{}'.format('/password_change/done')),
        (r'^/wikilegis/accounts/logout(.*)$',
            r'{}\1'.format('/account/logout')),
        (r'^/wikilegis/widget/login(.*)$', r'{}\1'.format('/widget/login')),
        (r'^/wikilegis/widget/signup(.*)$', r'{}\1'.format('/widget/signup')),
    )

    def get_proxy_request_headers(self, request):
        headers = super(ColabWikilegisPluginProxyView,
                        self).get_proxy_request_headers(request)

        if request.user.is_authenticated():
            headers["Auth-user"] = request.user.username

        return headers
