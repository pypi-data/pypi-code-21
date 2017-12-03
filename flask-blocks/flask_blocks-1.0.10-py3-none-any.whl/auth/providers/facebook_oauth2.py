import uuid
from . import OAuth2


class FacebookInfo:
    def __init__(self, scopes):
        self._scopes = scopes

    @property
    def name(self):
        return "facebook"

    @property
    def request_token_params(self):
        return {
            "scope": self._scopes,
            "auth_type": "reauthenticate",
            "auth_nonce": uuid.uuid4().hex,
        }

    @property
    def base_url(self):
        return "https://graph.facebook.com/"

    @property
    def access_token_method(self):
        return "GET"

    @property
    def access_token_url(self):
        return "/oauth/access_token"

    @property
    def authorize_url(self):
        return "https://www.facebook.com/dialog/oauth"

    @property
    def user_info_key(self):
        return "/me?fields=name,email"

    def process_user_info(self, user):
        return {
            "source": {
                "name": "facebook-oauth2",
                "version": 1
            },
            "id": user["id"],
            "name": user["name"],
            "email": user.get("email"),
            "picture": "https://graph.facebook.com/%s/picture?type=large" % (
                user["id"],),
        }


class FacebookOAuth2(OAuth2):
    def __init__(
            self, client_id, client_secret, return_uri="/", scopes=["email"]):
        for scope in scopes:
            if "," in scope:
                raise ValueError(
                    'The scope "%s" cannot contain a comma.' % (scope,))

        super().__init__(
            FacebookInfo(), client_id, client_secret, return_uri)
