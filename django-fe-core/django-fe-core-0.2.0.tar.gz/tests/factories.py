# -*- coding:utf-8 -*-
import uuid

import factory
from fe_core.models import User, Entity
from oauth2_provider.models import AccessToken, Application


class EntityFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'Entidade Nome: {0}'.format(n))

    class Meta:
        model = Entity


class UserFactory(factory.django.DjangoModelFactory):
    entity = factory.SubFactory(EntityFactory)
    email = factory.Sequence(lambda n: u'{0}@test.com'.format(n))
    is_staff = False
    is_active = True

    class Meta:
        model = User

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


class ApplicationFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    client_type = Application.CLIENT_PUBLIC
    authorization_grant_type = Application.GRANT_PASSWORD

    class Meta:
        model = Application


class AccessTokenFactory(factory.django.DjangoModelFactory):
    token = factory.Sequence(lambda n: str(uuid.uuid4()))
    user = factory.SubFactory(UserFactory)
    expires = factory.Faker('date_time_this_year', before_now=False, after_now=True)
    application = factory.SubFactory(ApplicationFactory)

    class Meta:
        model = AccessToken
