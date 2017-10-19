from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from push_notifications.models import APNSDevice, GCMDevice
from .base import NotificationBase
from .models import NotificationReceipt

User = get_user_model()


class NotificationClient(object):
    def get_devices(self, users):
        return APNSDevice.objects.filter(user__in=users), GCMDevice.objects.filter(user__in=users)

    def create_receipt(self, notification, user):
        return NotificationReceipt(payload=notification, user=user)

    def send_notification(self, notification, users):
        assert isinstance(notification, NotificationBase)
        assert isinstance(users, QuerySet)
        assert users.model is User

        apns_devices, gcm_devices = self.get_devices(users)
        try:
            apns_devices.send_message(notification.message, **notification.additional_data)
            gcm_devices.send_message(notification.message, **notification.additional_data)
        except Exception as e:
            pass

        NotificationReceipt.objects.bulk_create(
            [self.create_receipt(notification=notification, user=user) for user in users]
        )
