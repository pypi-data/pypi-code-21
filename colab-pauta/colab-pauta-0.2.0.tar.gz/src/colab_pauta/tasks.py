from colab_pauta.views import ColabPautaProxyView


def login_user(sender, user, request, **kwargs):
    proxy_view = ColabPautaProxyView()
    response = proxy_view.dispatch(request, '')
    session = response.cookies.get('pauta_session')
    request.COOKIES.set('pauta_session', session.value)


def logout_user(sender, user, request, **kwargs):
    request.COOKIES.delete('pauta_session')
