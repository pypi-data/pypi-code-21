from colab_wikilegis.views import ColabWikilegisPluginProxyView


def login_user(sender, user, request, **kwargs):
    proxy_view = ColabWikilegisPluginProxyView()
    response = proxy_view.dispatch(request, '')
    session = response.cookies.get('wikilegis_session')
    request.COOKIES.set('wikilegis_session', session.value)


def logout_user(sender, user, request, **kwargs):
    request.COOKIES.delete('wikilegis_session')
