# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.forms.fields import CharField
from django.utils.translation import ugettext_lazy as _

from phonenumber_field.phonenumber import to_python


def _process_phone(value, recurse=True):
    if value and isinstance(value, str):
        if value.startswith('8'):
            value = '+7' + value[1:]

    phone_number = to_python(value)
    if phone_number and phone_number.is_valid():
        return phone_number

    if recurse and value and isinstance(value, str):
        return _process_phone('+7' + value, recurse=False)


def validate_international_phonenumber(value):
    phone_number = _process_phone(value)
    if not phone_number:
        raise ValidationError('Введенный телефонный номер невалиден')


class ShopPhoneNumberField(CharField):
    default_error_messages = {
        'invalid': _('Пожалуйста, введите коррестный номер телефона'),
    }
    default_validators = [validate_international_phonenumber]

    def __init__(self, *args, **kwargs):
        super(ShopPhoneNumberField, self).__init__(*args, **kwargs)
        self.widget.input_type = 'tel'

    def to_python(self, value):
        phone_number = _process_phone(value)
        if not phone_number:
            raise ValidationError(self.error_messages['invalid'])
        return phone_number
