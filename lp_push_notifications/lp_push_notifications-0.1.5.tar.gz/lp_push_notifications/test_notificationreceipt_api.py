from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

User = get_user_model()


class NotificationTestCase(TestCase):
    fixtures = ['users', 'notificationreceipts']

    def setUp(self):
        self.client = APIClient()

    def authenticate(self, user=None):
        self.client.credentials()
        if user:
            token, created = Token.objects.get_or_create(user=user)
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def list(self, **kwargs):
        return self.client.get(
            reverse('notificationreceipts_list'),
            format='json',
            **kwargs
        )

    @staticmethod
    def get_default_user():
        return User.objects.get(id=1)


class NotificationReceiptListTestCase(NotificationTestCase):
    def setUp(self):
        super(NotificationReceiptListTestCase, self).setUp()
        self.user = self.get_default_user()

    def test_list_response(self):
        self.authenticate(user=self.user)
        response = self.list()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
