import flask
import flask_oauthlib
import flask_oauthlib.client


class OAuth2:
    def __init__(
            self, provider, client_id, client_secret, scheme, return_uri="/"):
        if not client_id:
            raise ValueError("The client_id value is missing.")

        if not client_secret:
            raise ValueError("The client_secret value is missing.")

        self.provider = provider
        self.client_id = client_id
        self.client_secret = client_secret
        self.return_uri = return_uri
        self.scheme = scheme

    def create(self, auth_blueprint):
        oauth = flask_oauthlib.client.OAuth(auth_blueprint)
        self.oauth_app = oauth.remote_app(
            self.provider.name,
            consumer_key=self.client_id,
            consumer_secret=self.client_secret,
            request_token_params=self.provider.request_token_params,
            base_url=self.provider.base_url,
            request_token_url=None,
            access_token_method=self.provider.access_token_method,
            access_token_url=self.provider.access_token_url,
            authorize_url=self.provider.authorize_url,
        )

        self.user_session_key = "user"
        self.token_session_key = "oauth_token"

        if self.oauth_app:
            @self.oauth_app.tokengetter
            def get_oauth_token():
                return flask.session.get(self.token_session_key)

    def login(self):
        return self.oauth_app.authorize(
            callback=flask.url_for(
                "auth.authorized", _external=True, _scheme=self.scheme))

    def logout(self):
        flask.session.pop(self.user_session_key)
        flask.session.pop(self.token_session_key)
        return flask.redirect(self.return_uri, code=302)

    def authorized(self, onauthorizing=None):
        resp = self.oauth_app.authorized_response()
        if resp is None:
            return "Access denied. Reason: %s. Error: %s." % (
                flask.request.args["error_reason"],
                flask.request.args["error_description"]
            ), 403

        if isinstance(resp, flask_oauthlib.client.OAuthException):
            raise resp

        flask.session[self.token_session_key] = (resp["access_token"], "")

        user = self.oauth_app.get(self.provider.user_info_key).data
        user_info = self.provider.process_user_info(user)

        if onauthorizing:
            custom_response = onauthorizing(user_info)
            if custom_response:
                return custom_response

        flask.session[self.user_session_key] = user_info
        return flask.redirect(self.return_uri, code=302)
