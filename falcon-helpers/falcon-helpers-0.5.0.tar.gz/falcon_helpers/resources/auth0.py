import falcon
import requests

from ..middlewares.jinja2 import Jinja2Response


class LoginFormResource:
    auth_required = False

    def __init__(self, client_url, client_id, callback_uri):
        self.client_url = client_url
        self.client_id = client_id
        self.callback_uri = callback_uri

    # Load form
    def on_get(self, req, resp):
        resp.context['template'] = Jinja2Response(
            'auth/login.html',
            auth0_config={
                'client_url': self.client_url,
                'client_id': self.client_id,
                'callback_uri': self.callback_uri,
            })


class LoginCallbackResource:
    auth_required = False

    def __init__(self, client_url, client_id, client_secret, callback_uri,
                 cookie_domain, secure_cookie, cookie_name='X-AuthToken',
                 cookie_max_age=(24 * 60 * 60), cookie_path='/',
                 redirect_uri='/dashboard'
                 ):
        self.client_url = client_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_uri = callback_uri
        self.redirect_uri = redirect_uri

        self.cookie_domain = cookie_domain
        self.secure_cookie = secure_cookie
        self.cookie_name = cookie_name
        self.cookie_max_age = cookie_max_age
        self.cookie_path = cookie_path

    def on_get(self, req, resp):
        try:
            auth_code = req.params['code']
        except KeyError:
            raise falcon.HTTPForbidden('Forbidden', 'Missing access code')

        data = self.get_user_data(auth_code)

        self.set_cookie_contents(resp, data)
        resp.set_header('Location', self.redirect_uri)
        resp.status = falcon.HTTP_302

    def get_user_data(self, auth_code):
        token = requests.post(
            f'https://{self.client_url}/oauth/token',
            data={
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': auth_code,
                'redirect_uri': self.callback_uri,
            })

        if not token.ok:
            raise falcon.HTTPTemporaryRedirect('/auth/login')

        return token.json()

    def set_cookie_contents(self, resp, data):
        resp.set_cookie(self.cookie_name,
                        data['id_token'],
                        max_age=self.cookie_max_age,
                        secure=self.secure_cookie,
                        path=self.cookie_path,
                        domain=self.cookie_domain)


class LogoutResource:
    auth_required = False

    def __init__(self, cookie_domain, secure_cookie, cookie_name='X-AuthToken',
                 cookie_path='/'):
        self.cookie_domain = cookie_domain
        self.secure_cookie = secure_cookie

        self.cookie_name = cookie_name
        self.cookie_path = cookie_path

    def on_get(self, req, resp):
        resp.set_cookie(self.cookie_name, '', secure=self.secure_cookie,
                        path=self.cookie_path, domain=self.cookie_domain)

        resp.status = falcon.HTTP_302
        resp.set_header('Location', '/auth/login')
