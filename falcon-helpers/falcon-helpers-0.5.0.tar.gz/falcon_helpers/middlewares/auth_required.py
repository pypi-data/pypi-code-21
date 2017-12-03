import falcon
import jwt


def _default_failed(reason):
    raise falcon.HTTPFound('/auth/login')


class ConfigurationError(Exception):
    pass


class AuthRequiredMiddleware:
    """Requires a cookie be set with a valid JWT or fails

    Example:
        import falcon
        from falcon_helpers.middlewares.auth_required import AuthRequiredMiddleware

        class Resource:
            auth_required = True

            def on_get(self, req, resp):
                # ...

        def when_fails_auth(reason):


        api = falcon.API(
            middleware=[
                AuthRequiredMiddleware(
                    'your-audience',
                    'a-really-great-random-string')
            ]
        )

        api.add_route('/', Resource())

    Attributes:
        audience: (string) A string audience which is passed to the JWT decoder

        secret: (string) A secret key to verify the token

        when_fails: (function) A function to execute when the authentication
            fails

        cookie_name: (string) the name of the cookie to look for

        resource_param: (string) the name of the paramater to look for on the
            resource to activate this middleware

    """

    def __init__(self, audience, secret=None, pubkey=None, when_fails=None,
                 cookie_name='X-AuthToken', resource_param='auth_required',
                 always=False, not_for=None):
        self.always = always
        self.audience = audience
        self.cookie_name = cookie_name
        self.failed_action = when_fails or _default_failed
        self.pubkey = pubkey
        self.resource_param = resource_param
        self.secret = secret
        self.not_for = not_for if not_for else []

        if (self.pubkey is not None
            and not self.pubkey.startswith('ssh-rsa')):
            raise ConfigurationError(
                'A public key for HS256 encoding must be in PEM Format')

    def verify_request(self, req):
        token = req.cookies.get(self.cookie_name, False)

        if not token:
            self.failed_action(Exception('Missing Token'))

        try:
            header = jwt.get_unverified_header(token)
        except jwt.exceptions.DecodeError as e:
            return self.failed_action(e)

        (type_, verify_with) = (('public key', self.pubkey)
                                if header['alg'] == 'RS256'
                                else ('secret key', self.secret))

        if verify_with is None:
            raise ConfigurationError('You must pass the correct verification'
                                     f' type for this algorithm.'
                                     f' {header["alg"]} requires a {type_}.')

        try:
            results = jwt.decode(token, verify_with, audience=self.audience)
        except jwt.exceptions.ExpiredSignatureError as e:
            self.failed_action(e)
        except jwt.exceptions.DecodeError as e:
            self.failed_action(e)

        req.context['auth_token_contents'] = results

    def process_request(self, req, resp):
        if self.always and req.path not in self.not_for:
            self.verify_request(req)


    def process_resource(self, req, resp, resource, params):
        required = getattr(resource, self.resource_param, True)

        if required:
            self.verify_request(req)
