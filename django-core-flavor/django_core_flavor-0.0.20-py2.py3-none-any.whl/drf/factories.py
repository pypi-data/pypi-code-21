import factory

from django.utils.timezone import utc
from .. import settings as core_settings


class ApplicationFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(core_settings.CORE_FLAVOR_USER_FACTORY)

    class Meta:
        model = 'oauth2_provider.Application'


class AccessTokenFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(core_settings.CORE_FLAVOR_USER_FACTORY)
    application = factory.SubFactory(ApplicationFactory)
    token = factory.Faker('text')

    expires = factory.Faker(
        'date_time_between',
        start_date='+1m',
        end_date='+2m',
        tzinfo=utc
    )

    class Meta:
        model = 'oauth2_provider.AccessToken'
