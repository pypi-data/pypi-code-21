import flask
import requests
from wtforms.fields import Field
from wtforms.validators import ValidationError
from wtforms.widgets.core import HTMLString

from manhattan.forms.validators import ErrorMessage

__all__ = ['ReCAPTCHAField']


class ReCAPTCHAWidget:
    """
    A widget that will render a Google reCAPTCHA field.
    """

    TEMPLATE = '''
<div class="g-recaptcha" data-sitekey="{site_key}"></div>
<script src="https://www.google.com/recaptcha/api.js" async defer></script>
    '''.strip()

    def __call__(self, field, **kwargs):
        kwargs.setdefault('template', self.TEMPLATE)
        return HTMLString(kwargs['template'].format(site_key=field.site_key))


class ReCAPTCHAField(Field):
    """
    A `Field` designed for implementing Google's reCAPTCHA service/widget.
    """
    widget = ReCAPTCHAWidget()

    # The Google reCAPTCHA service's API endpoint
    API_ENDPOINT = 'https://www.google.com/recaptcha/api/siteverify'

    def __init__(self, label=None, validators=None, secret_key=None,
            site_key=None, api_endpoint=None, **kwargs):

        super().__init__(label, validators, **kwargs)

        # The key sent to the Google API along with the user's submission when
        # testing the user is human (server-side).
        self.secret_key = secret_key

        # The key used when displaying the ReCAPTCHA widget (client-side)
        self.site_key = site_key

        # The API endpoint to call to validate a user response
        self.api_endpoint = api_endpoint or self.API_ENDPOINT

        # A cache of CAPTCHA validation result, we can only perform the
        # validation request once per submission and so we cache the results in
        # case validate is called against the field multiple times.
        self._cache = None

    def populate_obj(self, *args):
        """Don't populate objects with the CSRF token"""
        pass

    def pre_validate(self, form):
        """Handle validation of the CAPTCHA"""

        # Check if we have a cached response from Google
        if not self._cache:

            # Attempt to get the remote IP address
            ip_addr = None
            if flask.request:
                ip_addr = flask.request.remote_addr
                if 'X-Forwarded-For' in flask.request.headers:
                    ip_addr = flask.request.headers\
                            .getlist('X-Forwarded-For')[0].rpartition(' ')[-1]

            # Validate the user's submission with Google
            self._cache = requests.post(
                self.api_endpoint,
                data={
                    'secret': self.secret_key,
                    'response': self.data,
                    'remoteip': ip_addr
                    }
                )

        # If the the response indicates a failure raise a validation error
        # containing details of the failure.
        if not self._cache.json()['success']:
            message = ErrorMessage(
                self.gettext('CAPTCHA test failed'),
                self,
                error_codes=self._cache.json().get('error-codes', None)
                )
            raise ValidationError(message)

    def process(self, formdata, data=None):
        # Get the client-side token received from Google (the name of the field
        # is fixed).
        self.data = None
        if formdata:
            self.data = formdata.get('g-recaptcha-response', None)
