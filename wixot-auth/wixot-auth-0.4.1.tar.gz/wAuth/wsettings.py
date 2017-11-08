import os
from django.conf import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOCIAL_AUTH_URL_NAMESPACE = 'social'

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'social_core.pipeline.social_auth.associate_by_email',
)

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [

'https://www.googleapis.com/auth/userinfo.profile'
]

SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'wlogged'
SOCIAL_AUTH_LOGIN_URL = 'wlogged'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = 'wlogged'

for i in settings.TEMPLATES:
    if i['BACKEND'] == 'django.template.backends.django.DjangoTemplates':
        social_auth_context_processors_one = 'social_django.context_processors.backends'
        social_auth_context_processors_two ='social_django.context_processors.login_redirect'
        i['OPTIONS']['context_processors'].append(social_auth_context_processors_one)
        i['OPTIONS']['context_processors'].append(social_auth_context_processors_two)


INSTALLED_APPS = settings.INSTALLED_APPS + ['social_django']
MIDDLEWARE = settings.MIDDLEWARE + ['social_django.middleware.SocialAuthExceptionMiddleware',]

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = settings.W_GOOGLE_KEY
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = settings.W_GOOGLE_SECRET

