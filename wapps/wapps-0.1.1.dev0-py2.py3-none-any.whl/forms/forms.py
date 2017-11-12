import logging

import requests

from django.conf import settings
from django.forms import Form
from django.forms.fields import FileField
from django.utils.translation import ugettext_lazy as _
from wagtail.wagtailforms.forms import FormBuilder as WagtailFormBuilder
from wagtail.wagtailimages.fields import WagtailImageField

log = logging.getLogger(__name__)


class WappsForm(Form):
    '''Base form for used by FormBuilder'''
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)

    def _post_clean(self):
        self.verify_recaptcha()

    def verify_recaptcha(self):
        '''Challenge recaptcha response'''
        if not self.recaptcha:
            return

        response = self.data.get('g-recaptcha-response')
        if not response:
            self.add_error(None, _("You don't seems to be human"))
        try:
            r = requests.post('https://www.google.com/recaptcha/api/siteverify',
                             {'secret': settings.RECAPTCHA_PRIVATE_KEY, 'response': response},
                             timeout=5)
            r.raise_for_status()
        except requests.RequestException as e:
            log.exception('Unable to validate reCaptcha')
            self.add_error(None, _('Connection to reCaptcha server failed'))
            return

        json_response = r.json()

        if bool(json_response['success']):
            return

        if 'error-codes' in json_response:
            codes = json_response['error-codes']
            if 'missing-input-secret' in codes or 'invalid-input-secret' in codes:
                log.exception('Invalid reCaptcha secret key detected')
                self.add_error(None, _('Connection to reCaptcha server failed'))
            else:
                self.add_error(None, _('reCaptcha invalid or expired, try again'))
        else:
            log.exception('No error-codes received from Google reCaptcha server')
            raise self.add_error(None, _('reCaptcha response from Google not valid, try again'))


class FormBuilder(WagtailFormBuilder):
    def __init__(self, fields, **kwargs):
        self.recaptcha = kwargs.pop('recaptcha')
        super(FormBuilder, self).__init__(fields)

    # @property
    # def formfields(self):
    #     formfields = super(FormBuilder, self).formfields
    #
    #     if self.recaptcha_enabled:
    #         recaptcha_attrs = get_forms_setting('RECAPTCHA_ATTRS')
    #         formfields['recaptcha'] = ReCaptchaField(attrs=recaptcha_attrs)
    #
    #     return formfields

    def create_image_upload_field(self, field, options):
        return WagtailImageField(**options)

    def create_file_upload_field(self, field, options):
        return FileField(**options)

    FIELD_TYPES = WagtailFormBuilder.FIELD_TYPES
    FIELD_TYPES.update({
        # 'image': create_image_upload_field,
        'file': create_file_upload_field,
    })

    def get_form_class(self):
        kwargs = self.formfields
        kwargs['recaptcha'] = self.recaptcha
        return type(str('WappsForm'), (WappsForm,), kwargs)
