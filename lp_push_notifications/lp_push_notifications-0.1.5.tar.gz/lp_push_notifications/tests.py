from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.test import TestCase
from .client import NotificationClient
from .models import NotificationReceipt
from .base import FormattedNotification

User = get_user_model()


class NotificationReceiptTestCase(TestCase):
    fixtures = ['users']

    def setUp(self):
        self.user = User.objects.get(id=1)

    def test_can_create_notification_receipt(self):
        count = NotificationReceipt.objects.count()
        NotificationReceipt.objects.create(user=self.user)
        self.assertGreater(NotificationReceipt.objects.count(), count)


class NotificationClientTestCase(TestCase):
    fixtures = ['users']

    def setUp(self):
        self.users = User.objects.all()
        self.notification = FormattedNotification()
        self.client = NotificationClient()

    def test_send_requires_user_queryset(self):
        try:
            self.client.send_notification(notification=self.notification, users=None)
            self.fail('Send Notification allowed non-queryset argument for users')
        except Exception:
            pass

        try:
            self.client.send_notification(notification=self.notification, users=QuerySet())
            self.fail('Send Notification allowed non-User queryset argument for users')
        except Exception:
            pass

        try:
            self.client.send_notification(notification=self.notification, users=self.users)
        except Exception as e:
            self.fail('Notification Failed to Send: %s' % e)

    def test_send_require_notification_class(self):
        try:
            self.client.send_notification(notification=None, users=self.users)
            self.fail('Send Notification allowed None notification object')
        except Exception:
            pass

        try:
            self.client.send_notification(notification=self.notification, users=self.users)
        except Exception as e:
            self.fail('Notification Failed to Send: %s' % e)

    def test_send_creates_receipt(self):
        count = NotificationReceipt.objects.count()
        self.client.send_notification(notification=self.notification, users=self.users)
        self.assertGreater(NotificationReceipt.objects.count(), count)
