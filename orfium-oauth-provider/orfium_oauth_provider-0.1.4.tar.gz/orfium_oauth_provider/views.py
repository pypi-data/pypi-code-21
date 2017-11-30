import requests
from django.contrib.auth.views import logout

from django.shortcuts import redirect, render
from django.conf import settings
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import OrfiumOAuth2Provider
from django.conf import settings

try:
    API_ORFIUM_ENDPOINT = settings.API_ORFIUM_ENDPOINT.split('/v1')[0]
except AttributeError:
    API_ORFIUM_ENDPOINT = 'https://api.orfium.com'

# get the session cookie from the api endpoint
SESSION_COOKIE_DOMAIN = '.'.join(
        [''] +
        API_ORFIUM_ENDPOINT.
        replace('https://', '').
        replace('http://', '').
        split('.')[1:]
    ). \
    split(':')[0]


class OrfiumOAuth2CallbackView(OAuth2CallbackView):

    def dispatch(self, request):
        result = super(OrfiumOAuth2CallbackView, self).dispatch(request)

        # redirect to the default redirect page instead of connections
        try:
            if result.url.endswith('/social/connections/'):
                return redirect(settings.LOGIN_REDIRECT_URL)
        except AttributeError:
            pass

        return result


class OrfiumOAuth2Adapter(OAuth2Adapter):
    provider_id = OrfiumOAuth2Provider.id
    access_token_url = '%s/oauth/token/' % API_ORFIUM_ENDPOINT
    authorize_url = '%s/oauth/authorize/' % API_ORFIUM_ENDPOINT
    profile_url = '%s/v1/my/info/' % API_ORFIUM_ENDPOINT
    # See:
    # http://developer.linkedin.com/forum/unauthorized-invalid-or-expired-token-immediately-after-receiving-oauth2-token?page=1 # noqa
    access_token_method = 'POST'

    def complete_login(self, request, app, token, **kwargs):
        extra_data = self.get_user_info(token)
        return self.get_provider().sociallogin_from_response(
            request, extra_data)

    def get_user_info(self, token):
        resp = requests.get(self.profile_url,
                            headers={'Authorization': 'Bearer %s' % token.token})
        return resp.json()['user_info']


oauth2_login = OAuth2LoginView.adapter_view(OrfiumOAuth2Adapter)
oauth2_callback = OrfiumOAuth2CallbackView.adapter_view(OrfiumOAuth2Adapter)


def logout_view(request):
    # logout from the dashboard
    logout(request)

    # we need an intermediate page in order to first delete the sessionid cookie
    response = render(request, 'api-logout-redirect.html', {
        'API_LOGOUT_URL': '%s/accounts/logout/' % API_ORFIUM_ENDPOINT
    })

    # logout from the main website as well
    # temporarily, until all authentications is handled by api.orfium.com
    response.delete_cookie('sessionid', domain=SESSION_COOKIE_DOMAIN)

    return response
