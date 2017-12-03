from . import OAuth2


class GoogleInfo:
    def __init__(self, scopes):
        self._scopes = scopes

    @property
    def name(self):
        return "google"

    @property
    def request_token_params(self):
        return {"scope": self._scopes}

    @property
    def base_url(self):
        return "https://www.googleapis.com/oauth2/v1/"

    @property
    def access_token_method(self):
        return "POST"

    @property
    def access_token_url(self):
        return "https://accounts.google.com/o/oauth2/token"

    @property
    def authorize_url(self):
        return "https://accounts.google.com/o/oauth2/auth"

    @property
    def user_info_key(self):
        return "userinfo"

    def process_user_info(self, user):
        return {
            "source": {
                "name": "google-oauth2",
                "version": 1
            },
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "picture": user["picture"],
        }


class GoogleOAuth2(OAuth2):
    def __init__(
            self, client_id, client_secret, scheme,
            return_uri="/", scopes=["email"]):
        for scope in scopes:
            if "," in scope:
                raise ValueError(
                    'The scope "%s" cannot contain a comma.' % (scope,))

        super().__init__(
            GoogleInfo(scopes), client_id, client_secret, scheme, return_uri)
