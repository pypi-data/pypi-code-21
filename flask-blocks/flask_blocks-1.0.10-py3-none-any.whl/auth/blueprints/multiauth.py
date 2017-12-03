import flask


def create_auth(
        providers,
        onlogin=None,
        onlogout=None,
        onauthorizing=None,
        onauthorized=None):
    auth = flask.Blueprint("auth", __name__)
    for name, provider in providers.items():
        provider.create(auth)

    @auth.route('/login/<provider_name>')
    def login(provider_name):
        flask.session["auth_provider"] = provider_name
        result = providers[provider_name].login()

        if onlogin:
            onlogin(flask.request, result)

        return result

    @auth.route('/logout')
    def logout():
        provider_name = flask.session["auth_provider"]
        result = providers[provider_name].logout()

        if onlogout:
            onlogout(flask.request, result)

        return result

    @auth.route('/authorized')
    def authorized():
        provider_name = flask.session["auth_provider"]
        result = providers[provider_name].authorized(onauthorizing)

        if onauthorized:
            onauthorized(flask.request, result)

        return result

    return auth
