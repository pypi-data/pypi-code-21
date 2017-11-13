from . import constants


class Config(object):
    CUSTOM_PASSWORD_REQUIREMENTS = {}
    CUSTOM_EMAIL_VERIFICATION = {}
    CUSTOM_SIMPLE_ACCOUNTS_APP_PATHS = {}
    CUSTOM_EMAIL_VERIFICATION_TEMPLATE = {}

    PASSWORD_REQUIREMENTS = {
        'has_length':           {'default': True, 'min_value': 16},
        'has_number':           {'default': True, 'min_value': 4},
        'has_letter':           {'default': True, 'min_value': 4},
        'has_upper_case':       {'default': True, 'min_value': 4},
        'has_lower_case':       {'default': True, 'min_value': 4},

        'has_special_character':
            {'default': True, 'min_value': 2, 'values': constants.OWASP_APPROVED_SPECIAL_CHARACTERS},
    }

    EMAIL_VERIFICATION = {
        'enabled': True,
        'email_template': 'basic',
        'hours_verification_is_valid': 24,
        'subject': 'Email Verification',
        'sender': 'admin@myapp.com'
    }

    EMAIL_VERIFICATION_TEMPLATE = {
        'style': 'bubble_gum',

        'success_title': "Email verification is valid",
        'success_message': "Your email address has been verified.",

        'fail_title': "Email verification Is Invalid",
        'fail_message': "Your verification link has expired or is not valid.",

        'return_link': '/',
        'return_link_text': 'Return to Home'
    }

    SITE_ADDRESS = None

    SIMPLE_ACCOUNTS_APP_PATHS = {
        'sign_up': '/sign-up',
        'verify_email': '/verify-email',
        'log_in': '/log-in',
        'log_out': '/log-out',
        'change_email': '/change_email',
        'change_password': '/change_password',
        'delete_account': '/delete-account',
    }
