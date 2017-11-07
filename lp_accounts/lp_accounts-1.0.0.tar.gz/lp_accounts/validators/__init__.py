from ..models import User
from .facebook import FacebookValidator
from .google import GoogleValidator
from .base import BaseValidator

VALIDATORS = {
    User.TYPE_GOOGLE: GoogleValidator,
    User.TYPE_FACEBOOK: FacebookValidator
}


def get_validator(account_type):
    if account_type in VALIDATORS.keys():
        return VALIDATORS[account_type]()
    else:
        return BaseValidator()
