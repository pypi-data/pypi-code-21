from appconf import AppConf
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FormsConfig(AppConfig):
    name = 'wapps.forms'
    label = 'forms'
    verbose_name = 'Forms'


class FormsSettings(AppConf):
    '''Wapps forms default settings'''
    SUCCESS_MSG = _('Thank you, the form has been submitted.')
    ERROR_MSG = _('There was an error processing the form')
    UPLOAD_ROOT = 'forms'

    class Meta:
        prefix = 'wapps_forms'


class RecaptchaSettings(AppConf):
    '''Wapps forms default recaptcha settings'''
    #: Default recaptcha public key, dev key
    PUBLIC_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
    #: Default recaptcha private key, dev key
    PRIVATE_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'

    class Meta:
        prefix = 'recaptcha'
