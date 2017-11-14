from ..models import User
from .base import BaseValidator
from .facebook import FacebookValidator
from .github import GithubValidator
from .google import GoogleValidator
from .linkedin import LinkedInValidator

VALIDATORS = {
    User.TYPE_GOOGLE: GoogleValidator,
    User.TYPE_FACEBOOK: FacebookValidator,
    User.TYPE_GITHUB: GithubValidator,
    User.TYPE_LINKEDIN: LinkedInValidator
}


def get_validator(account_type):
    if account_type in VALIDATORS.keys():
        return VALIDATORS[account_type]()
    else:
        return BaseValidator()
