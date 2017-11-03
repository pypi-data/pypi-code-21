from datetime import timedelta

from dj_core.config import Config as BaseConfig, DefaultProxy


class Config(BaseConfig):
    defaults = BaseConfig.defaults.copy()
    defaults.update({
        'ACCOUNT_AUTHENTICATION_METHOD': 'email',
        'ACCOUNT_EMAIL_REQUIRED': True,
        'ACCOUNT_EMAIL_VERIFICATION': 'none',
        'ACCOUNT_USER_MODEL_USERNAME_FIELD': None,
        'ACCOUNT_USERNAME_REQUIRED': False,
        'ACCOUNT_REGISTRATION': 'enabled',
        'REST_USE_JWT': True,
        'SWAGGER_SETTINGS': {'api_version': '1'},
        'JWT_AUTH': {
            'JWT_EXPIRATION_DELTA': timedelta(hours=24),
            'JWT_AUTH_HEADER_PREFIX': 'Token',
        },
        'REST_FRAMEWORK': DefaultProxy({}, 'get_drf_settings'),
        'REST_AUTH_SERIALIZERS': DefaultProxy({}, 'get_rest_auth_serializers'),
    })
    defaults.INSTALLED_APPS_REQUIRED = [
        'dj_core_drf',
        'rest_framework',
        'rest_framework.authtoken',
        'rest_framework_swagger',
        'rest_auth',
        'allauth',
        'allauth.account',
        'rest_auth.registration',
        'revproxy',
        'django_filters',
    ] + defaults.INSTALLED_APPS_REQUIRED

    def get_drf_settings(self, settings):  # pylint: disable=unused-argument,no-self-use
        return {
            'DEFAULT_PERMISSION_CLASSES': [
                'rest_framework.permissions.IsAuthenticatedOrReadOnly'
            ],
            'DEFAULT_AUTHENTICATION_CLASSES': [
                'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
                'rest_framework.authentication.BasicAuthentication',
                'rest_framework.authentication.SessionAuthentication',
            ],
            'DEFAULT_PAGINATION_CLASS': 'dj_core_drf.pagination.ThousandMaxLimitOffsetPagination',
            'DEFAULT_FILTER_BACKENDS': [
                'rest_framework_filters.backends.DjangoFilterBackend',
            ],
            'DEFAULT_METADATA_CLASS': 'dj_core_drf.metadata.ModelChoicesMetadata',
        }

    def get_rest_auth_serializers(self, settings):  # pylint: disable=unused-argument,no-self-use
        return {
            'USER_DETAILS_SERIALIZER': 'dj_core_drf.serializers.UserDetailsSerializer',
            'PASSWORD_RESET_SERIALIZER': 'dj_core_drf.serializers.PasswordResetSerializer',
            'LOGIN_SERIALIZER': 'dj_core_drf.serializers.LoginSerializer',
        }
