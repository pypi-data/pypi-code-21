from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    service_due = models.DateTimeField(null=True)
    max_clients = models.PositiveIntegerField(default=2)
    cur_clients = models.PositiveIntegerField(default=0)
    token = models.CharField(max_length=20)
    device_id = models.CharField(max_length=20) # 简化仅支持最后一台

    def is_in_service(self):
        return self.service_due and self.service_due > timezone.now()
