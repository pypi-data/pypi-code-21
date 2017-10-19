from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from push_notifications.models import APNSDevice, GCMDevice
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

User = get_user_model()


class DeviceTestCase(TestCase):
    fixtures = ['users']

    def setUp(self):
        super(DeviceTestCase, self).setUp()
        self.client = APIClient()

    def authenticate(self, user=None):
        self.client.credentials()
        if user:
            token, created = Token.objects.get_or_create(user=user)
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def register_apns_device(self, **kwargs):
        return self.client.post(
            reverse('create_apns_device'),
            format='json',
            **kwargs
        )

    def register_gcm_device(self, **kwargs):
        return self.client.post(
            reverse('create_gcm_device'),
            format='json',
            **kwargs
        )

    @staticmethod
    def get_default_user():
        return User.objects.get(id=1)


class APNSDeviceTestCase(DeviceTestCase):
    def setUp(self):
        super(APNSDeviceTestCase, self).setUp()
        self.user = self.get_default_user()
        self.data = {
            'registration_id': 'F165DC421E885CE7C5F798C9074B5218D2AFAF55F7D7D94A0EDCA4AE3DD7E4A1'
        }

    def test_can_register_device(self):
        self.authenticate(user=self.user)
        count = APNSDevice.objects.count()
        response = self.register_apns_device(data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertGreater(APNSDevice.objects.count(), count)


class GCMDeviceTestCase(DeviceTestCase):
    def setUp(self):
        super(GCMDeviceTestCase, self).setUp()
        self.user = self.get_default_user()
        self.data = {
            'registration_id': 'F165DC421E885CE7C5F798C9074B5218D2AFAF55F7D7D94A0EDCA4AE3DD7E4A1',
            'cloud_message_type': 'FCM'
        }

    def test_can_register_device(self):
        self.authenticate(user=self.user)
        count = GCMDevice.objects.count()
        response = self.register_gcm_device(data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertGreater(GCMDevice.objects.count(), count)
