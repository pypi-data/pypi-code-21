# -*- coding: utf-8 -*-
import json

from mock import patch

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from fcm_django.models import FCMDevice

from molo.core.tests.base import MoloTestCaseMixin


class NotificationsTestCase(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.client = Client()
        self.user = User.objects.create_user(
            username="tester",
            email="tester@example.com",
            password="0000")

    @patch('molo.pwa.utils.send_notification_to_fcm')
    def test_send_notification(self, send_notification_to_fcm):
        # test no devices exist
        self.assertEquals(FCMDevice.objects.all().count(), 0)
        # test that when view for registration id
        self.client.login(username='tester', password='0000')
        response = self.client.post(
            reverse('molo.pwa:registration-token'),
            json.dumps({"registration_id": "1234"},),
            content_type="application/json")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, 'Token Updated')
        self.assertEquals(FCMDevice.objects.all().count(), 1)
        self.user.profile.refresh_from_db()
        self.assertEquals(self.user.profile.fcm_registration_token, '1234')

        # test sending a notification
        send_notification_to_fcm(
            self.user, 'title', 'content', self.user.id)
        # it should not create another device
        self.assertEquals(FCMDevice.objects.all().count(), 1)
        send_notification_to_fcm.assert_called_once_with(
            self.user,
            'title',
            'content',
            self.user.pk)
