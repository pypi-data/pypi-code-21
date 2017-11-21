import requests

from django.shortcuts import redirect
from django.conf import settings
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import OrfiumOAuth2Provider


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
    access_token_url = 'https://api.orfium.com/oauth/token/'
    authorize_url = 'https://api.orfium.com/oauth/authorize/'
    profile_url = 'https://api.orfium.com/v1/my/info/'
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
