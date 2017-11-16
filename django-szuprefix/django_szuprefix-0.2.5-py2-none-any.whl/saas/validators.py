# -*- coding:utf-8 -*-
from django.core.validators import validate_email, validate_slug

__author__ = 'denishuang'

from django_szuprefix.utils import datautils
from django.core.validators import RegexValidator

import re

RE_NOT_ALPHA = re.compile(r"[^0-9a-zA-Z]")
RE_SPACE = re.compile(r"\s")


def format_half_year(v):
    if v>0 and v<70:
        return 2000+v
    elif v>=70 and v<100:
        return 1900+v
    return v


def format_not_require(v):
    if v == "":
        return None
    return v


def format_split_by_bracket(v):
    return unicode(v).split("(")[0]


def format_banjiao(value):
    if not isinstance(value, (str, unicode)):
        value = unicode(value)
    return datautils.strQ2B(value)


def format_upper(value):
    return value.upper()

format_not_float = datautils.not_float


def format_str_without_space(value):
    if value is not None:
        return RE_SPACE.sub("", unicode(value))


def format_alpha(value):
    return RE_NOT_ALPHA.sub("", value)



class BaseField(object):
    default_validators = []
    default_formaters = []
    name = "undefined"
    default_synonyms = []
    clear_space = True
    ignore_invalid = False
    no_duplicate = False

    def __init__(self, name=None, synonyms=[], formaters=[], validators=[]):
        self.name = name or self.name
        self._synonyms = self.default_synonyms + synonyms
        self._validators = self.default_validators + validators
        self._formaters = self.default_formaters + formaters

        if self.clear_space:
            self._formaters.append(format_str_without_space)

    def get_formaters(self):
        return self._formaters

    def get_validators(self):
        return self._validators

    def get_synonyms(self):
        return self._synonyms

    def _format(self, value):
        for f in self.get_formaters():
            value = f(value)
        return value

    def _validate(self, value):
        errors = []
        for f in self.get_validators():
            try:
                f(value)
            except Exception, e:
                errors.append(e.message)
        return errors

    def __call__(self, value):
        value = self._format(value)
        errors = self._validate(value)
        if errors and self.ignore_invalid:
            errors = []
            value = None
        return self.name, value, errors




class EmailField(BaseField):
    name = u"邮箱"
    default_synonyms = [u"EMAIL", u"电子邮箱", u"MAIL"]
    default_validators = [validate_email]
    default_formaters = [format_banjiao]
    ignore_invalid = True
    no_duplicate = True


field_email = EmailField()


class UseridField(BaseField):
    name = u"帐号"
    default_synonyms = [u"学号", u"工号"]
    default_validators = [validate_slug]
    default_formaters = [format_not_float, format_banjiao, format_str_without_space]


field_userid = UseridField()