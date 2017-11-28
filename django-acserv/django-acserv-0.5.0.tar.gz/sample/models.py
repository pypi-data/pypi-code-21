from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone


class User(AbstractUser):
    service_due = models.DateTimeField(null=True)
    max_sessions = models.PositiveIntegerField(default=2)

    def is_in_service(self):
        return self.service_due and self.service_due > timezone.now()


class ClientSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="client_sessions")
    device_id = models.CharField(max_length=128, unique=True, null=True)
    app = models.CharField(max_length=32, default='', blank=True)
    os = models.CharField(max_length=32, default='', blank=True)
    ip = models.GenericIPAddressField(default='', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def post_save(cls, sender, instance: 'ClientSession', raw, created, **kwargs):
        if raw:
            return


post_save.connect(ClientSession.post_save, sender=ClientSession)
