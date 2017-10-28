from django.conf import settings


CORE_FLAVOR_USER_FACTORY = getattr(
    settings,
    'CORE_FLAVOR_USER_FACTORY',
    'core_flavor.factories.UserFactory')

CORE_REQUEST_LOGGER_NAME = getattr(
    settings,
    'CORE_REQUEST_LOGGER_NAME',
    'django.request')
