from django.conf import settings
import sys


default_app_config = 'lp_accounts.apps.AccountConfig'

settings.INSTALLED_APPS += [
    'generic_relations',
]

# Flag for Testing Environment
settings.TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

# Extend Native User Model
settings.AUTH_USER_MODEL = 'lp_accounts.User'

# REST Framework Configuration
settings.REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    )
}

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

# Google Sign-In Integration
# https://developers.google.com/identity/sign-in/web/backend-auth
settings.LP_ACCOUNTS_GOOGLE_APP_ID = getattr(
    settings, 'LP_ACCOUNTS_GOOGLE_APP_ID', None)
settings.LP_ACCOUNTS_GOOGLE_VALIDATION_URL = getattr(
    settings, 'LP_ACCOUNTS_GOOGLE_VALIDATION_URL', 'https://www.googleapis.com/oauth2/v3/tokeninfo?access_token=%s')

# Facebook Login Integration
# https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow#checktoken
settings.LP_ACCOUNTS_FACEBOOK_APP_ID = getattr(
    settings, 'LP_ACCOUNTS_FACEBOOK_APP_ID', None)
settings.LP_ACCOUNTS_FACEBOOK_CLIENT_SECRET = getattr(
    settings, 'LP_ACCOUNTS_FACEBOOK_CLIENT_SECRET', None)
settings.LP_ACCOUNTS_FACEBOOK_VALIDATION_URL = getattr(
    settings, 'FACEBOOK_VALIDATION_URL', 'https://graph.facebook.com/debug_token?input_token=%s&access_token=%s|%s')

# Github Login Integration
# Docs:
# https://developer.github.com/apps/building-integrations/setting-up-a-new-integration/about-integrations/
# Example:
# https://simpleisbetterthancomplex.com/tutorial/2016/10/24/how-to-add-social-login-to-django.html
settings.LP_ACCOUNTS_GITHUB_APP_ID = getattr(
    settings, 'LP_ACCOUNTS_GITHUB_APP_ID', None)
settings.LP_ACCOUNTS_GITHUB_CLIENT_SECRET = getattr(
    settings, 'LP_ACCOUNTS_GITHUB_CLIENT_SECRET', None)
settings.LP_ACCOUNTS_GITHUB_VALIDATION_URL = getattr(
    settings, 'LP_ACCOUNTS_GITHUB_VALIDATION_URL', 'https://api.github.com/applications/%s/tokens/%s')

# LinkedIn Login Integration
# Docs:
# https://developer.linkedin.com/docs/oauth2
settings.LP_ACCOUNTS_LINKEDIN_APP_ID = getattr(
    settings, 'LP_ACCOUNTS_LINKEDIN_APP_ID', None)
settings.LP_ACCOUNTS_LINKEDIN_APP_SECRET = getattr(
    settings, 'LP_ACCOUNTS_LINKEDIN_APP_SECRET', None)
