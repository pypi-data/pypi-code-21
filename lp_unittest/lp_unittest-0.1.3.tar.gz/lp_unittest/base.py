from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class BaseRestUnitTest(TestCase):
    fixtures = []
    url = ''
    users = {}

    def setUp(self):
        self.client = APIClient()

    def authenticate(self, user=None):
        self.client.credentials()
        if user:
            token, created = Token.objects.get_or_create(user=user)
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    @staticmethod
    def modify_data(data={}, exclude=[], injections={}):
        data = {**data, **injections}
        for field in exclude:
            data.pop(field, None)

        return data

    def list(self, **kwargs):
        return self.client.get(
            reverse(self.url),
            format='json',
            **kwargs
        )

    def create(self, **kwargs):
        return self.client.post(
            reverse(self.url),
            format='json',
            **kwargs
        )

    def retrieve(self, pk, **kwargs):
        return self.client.get(
            reverse(self.url, kwargs={'pk': pk}),
            format='json',
            **kwargs
        )

    def update(self, pk, **kwargs):
        return self.client.patch(
            reverse(self.url, kwargs={'pk': pk}),
            format='json',
            **kwargs
        )

    def destroy(self, pk, **kwargs):
        return self.client.delete(
            reverse(self.url, kwargs={'pk': pk}),
            format='json'
            **kwargs
        )
