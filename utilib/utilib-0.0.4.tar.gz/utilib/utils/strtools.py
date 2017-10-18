from utilib.core import exceptions
import re
import string
import random


def is_phone(_str, raise_exception=False):
    """
    Determine if a string param is a phone number.
    """
    if re.match(r'^(\+86|)1[0-9]{10}$', _str):
        return True
    if raise_exception:
        raise exceptions.InvalidPhoneNumber
    return False


def is_email(_str, raise_exception=False):
    if re.match(
        r'^[0-9a-zA-Z_]+@[0-9a-zA-Z\-\u4e00-\u9fa5]'
        r'+\.(com|cn|com\.cn|edu\.cn|net)$',
            _str):
        return True
    if raise_exception:
        raise exceptions.InvalidEmailAddress
    return False


def is_username(_str, raise_exception=False):
    if re.match(r'^[A-Za-z][0-9a-zA-Z_]{5,15}$', _str):
        return True
    if raise_exception:
        raise exceptions.InvalidUsername
    return False


def is_chinese_name(_str, raise_exception=False):
    if re.match(r'^[\u4e00-\u9fa5]{2,}$', _str):
        return True
    if raise_exception:
        raise exceptions.InvalidChineseName
    return False


def is_password(_str, raise_exception=False):
    if re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d$@$!%*#?&.]{8,}$', _str):
        return True
    if raise_exception:
        raise exceptions.InvalidPassword
    return False


def gen_sms_vcode(size=6):
    return ''.join(random.choice(string.digits) for _ in range(size))


def gen_captcha(size=6):
    return ''.join(random.choice(string.ascii_letters +
                                 string.digits) for _ in range(size))


def gen_nonce_str(size=16):
    return ''.join(random.choice(string.ascii_letters +
                                 string.digits) for _ in range(size))


def to_str(_str):
    if isinstance(_str, bytes):
        return _str.decode()
    return str(_str)
