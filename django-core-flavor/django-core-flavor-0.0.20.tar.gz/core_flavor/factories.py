import factory

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.timezone import utc


USER_MODEL = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    email = factory.Faker('email')

    if hasattr(USER_MODEL, 'username'):
        username = factory.Faker('name')

    password = factory.PostGenerationMethodCall('set_password', 'password')

    last_login = factory.Faker(
        'date_time_between',
        start_date='-1y',
        tzinfo=utc)

    class Meta:
        model = settings.AUTH_USER_MODEL
        django_get_or_create = (USER_MODEL.USERNAME_FIELD,)


class AdminFactory(UserFactory):
    is_staff = True
