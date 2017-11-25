# -*- coding:utf-8 -*-
__author__ = 'denishuang'
from django.core.validators import RegexValidator
from django_szuprefix.saas.validators import BaseField, format_not_float, format_banjiao, format_split_by_bracket, \
    format_upper


class IDCardValidator(RegexValidator):
    message = u"身份证格式不对"
    regex = u"^[1-9]\d{5}(19|2\d)\d{2}((0[1-9])|(1[0-2]))(([0|1|2]\d)|3[0-1])\d{3}([0-9]|X)$"


valid_idcard = IDCardValidator()


class WeixinIDValidator(RegexValidator):
    message = u"微信号格式不对"
    regex = u"^[a-zA-Z][-_\w]+$"


valid_weixinid = WeixinIDValidator()


class MobileValidator(RegexValidator):
    message = u"手机格式不对"
    regex = u"^1[3-8]\\d{9}$"


valid_mobile = MobileValidator()


class HanNameValidator(RegexValidator):
    regex = u"^[\u4e00-\u9fa5]{2,}$"
    message = u"姓名格式不对"


valid_han_name = HanNameValidator()

valid_position = HanNameValidator(message=u"职位格式不对")


class QQValidator(RegexValidator):
    regex = "^\d{4,16}$"
    message = u"QQ格式不对"


valid_qq = QQValidator()


class MobileField(BaseField):
    name = u"手机"
    default_synonyms = [u"手机号", u"手机号码", u"联系电话"]
    default_validators = [valid_mobile]
    default_formaters = [format_not_float, format_banjiao]
    no_duplicate = True


field_mobile = MobileField()


class IDCardField(BaseField):
    name = u"身份证"
    default_synonyms = [u"身份证号", u"身份证号码"]
    default_validators = [valid_idcard]
    default_formaters = [format_not_float, format_banjiao, format_upper]
    ignore_invalid = True
    no_duplicate = True


field_idcard = IDCardField()


class WeixinIDField(BaseField):
    name = u"微信号"
    default_synonyms = [u"微信ID"]
    default_validators = [valid_weixinid]
    default_formaters = [format_not_float, format_banjiao]
    ignore_invalid = True
    no_duplicate = True


field_weixinid = WeixinIDField()


class HanNameField(BaseField):
    name = u"姓名"
    default_validators = [valid_han_name]
    default_formaters = [format_banjiao, format_split_by_bracket]


field_han_name = HanNameField()


class PositionField(BaseField):
    name = u"职位"
    default_validators = []


field_position = PositionField()


class QQField(BaseField):
    name = u"QQ"
    default_synonyms = [u"扣扣", u"QQ号"]
    default_validators = [valid_qq]
    default_formaters = [format_not_float, format_banjiao]
    ignore_invalid = True
    no_duplicate = True


field_qq = QQField()
