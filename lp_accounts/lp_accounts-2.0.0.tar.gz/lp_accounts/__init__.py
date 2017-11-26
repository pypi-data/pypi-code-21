from django.conf import settings
import sys


default_app_config = 'lp_accounts.apps.AccountConfig'

settings.INSTALLED_APPS += [
    'generic_relations',
    'oauth2_provider',
    'social_django',
    'rest_framework_social_oauth2',
]

# Flag for Testing Environment
settings.TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

# Extend Native User Model
settings.AUTH_USER_MODEL = 'lp_accounts.User'

# REST Framework Configuration
settings.REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework_social_oauth2.authentication.SocialAuthentication',
    )
}

# Social Auth Configuration
settings.TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'social_django.context_processors.backends',
    'social_django.context_processors.login_redirect',
]
settings.AUTHENTICATION_BACKENDS += [
    'rest_framework_social_oauth2.backends.DjangoOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

# Configure Templated Email
settings.TEMPLATED_EMAIL_TEMPLATE_DIR = getattr(
    settings, 'TEMPLATED_EMAIL_TEMPLATE_DIR', 'templated_email/')
settings.TEMPLATED_EMAIL_FILE_EXTENSION = getattr(
    settings, 'TEMPLATED_EMAIL_FILE_EXTENSION', 'email'
)

# Welcome Email Configuration
settings.LP_ACCOUNTS_WELCOME_EMAIL_ENABLED = getattr(
    settings, 'LP_ACCOUNTS_WELCOME_EMAIL_ENABLED', False)
settings.LP_ACCOUNTS_WELCOME_EMAIL_TEMPLATE = getattr(
    settings, 'LP_ACCOUNTS_WELCOME_EMAIL_TEMPLATE', 'welcome')
settings.LP_ACCOUNTS_WELCOME_EMAIL_SENDER = getattr(
    settings, 'LP_ACCOUNTS_WELCOME_EMAIL_SENDER', 'support@launchpeer.com')

# Reset Password Email Configuration
settings.LP_ACCOUNTS_PASSWORD_RESET_TEMPLATE = getattr(
    settings, 'LP_ACCOUNTS_FORGOT_PASSWORD_TEMPLATE', 'passwordreset'
)
settings.LP_ACCOUNTS_PASSWORD_RESET_SENDER = getattr(
    settings, 'LP_ACCOUNTS_PASSWORD_RESET_SENDER', 'support@launchpeer.com'
)
