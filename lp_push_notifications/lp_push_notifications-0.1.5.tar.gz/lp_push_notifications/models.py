from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class NotificationReceipt(models.Model):
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField(auto_now_add=True)
    has_read = models.BooleanField(default=False)
    payload = models.TextField(default='')
