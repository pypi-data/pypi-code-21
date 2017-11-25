from django.contrib.auth import get_user_model
from faker import Faker
from rest_framework.test import APIClient
from django.test.client import Client as DjangoTestClient


class AuthAdminClient(DjangoTestClient):
    user = None

    def init(self):
        """
        The `__init__` would be outside of the test transaction.
        """
        fake = Faker()
        user_ident = fake.user_name()
        self.user = get_user_model().objects.create(
            username=user_ident,
            email=user_ident + '@localhost',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            password=user_ident,
            is_superuser=True,
            is_staff=True,
        )
        super().force_login(self.user)


class AuthUserClient(DjangoTestClient):
    user = None

    def init(self):
        """
        The `__init__` would be outside of the test transaction.
        """
        fake = Faker()
        user_ident = fake.user_name()
        self.user = get_user_model().objects.create(
            username=user_ident,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=user_ident + '@localhost',
            password=user_ident,
        )
        super().force_login(self.user)


class ApiAuthAdminClient(APIClient, AuthAdminClient):
    pass
