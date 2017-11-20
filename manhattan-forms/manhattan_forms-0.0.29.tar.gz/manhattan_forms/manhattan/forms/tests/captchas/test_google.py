from datetime import date, time

import pytest
import requests
import requests_mock
from werkzeug.datastructures import MultiDict

from manhattan.forms import BaseForm
from manhattan.forms.captchas.google import ReCAPTCHAField


def test_recaptcha_field():
    """Support for Google reCAPTCHA field"""

    class MyForm(BaseForm):

        captcha = ReCAPTCHAField(
            secret_key='foo',
            site_key='bar'
            )

    with requests_mock.Mocker() as mock_req:

        # Test a valid submission
        mock_req.post(
            'https://www.google.com/recaptcha/api/siteverify',
            json={'success': True}
            )
        form = MyForm(MultiDict({'g-recaptcha-response': 'success'}))
        assert form.validate() == True

        # Test an invalid submission
        mock_req.post(
            'https://www.google.com/recaptcha/api/siteverify',
            json={
                'success': False,
                'error-codes': ['invalid-input-response']
                }
            )
        form = MyForm(MultiDict({'g-recaptcha-response': 'success'}))
        assert form.validate() == False
        error = form.errors['captcha'][0]
        assert str(error) == 'CAPTCHA test failed'
        assert error.error_codes == ['invalid-input-response']

def test_recaptcha_widget():
    """Render a Google reCAPTCHA field"""

    class MyForm(BaseForm):

        captcha = ReCAPTCHAField(
            secret_key='foo',
            site_key='bar'
            )

    form = MyForm()

    # Default template render
    assert form.captcha() == '''
<div class="g-recaptcha" data-sitekey="bar"></div>
<script src="https://www.google.com/recaptcha/api.js" async defer></script>
    '''.strip()

    # Custom template render
    template = '<div class="g-recaptcha" data-sitekey="{site_key}"></div>'
    assert form.captcha(template=template) == \
        '<div class="g-recaptcha" data-sitekey="bar"></div>'
