from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


# Create your models here.
class User(AbstractUser):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    account_id = models.PositiveIntegerField(null=True)
    account = GenericForeignKey('content_type', 'account_id')

    def __str__(self):
        return self.username


class BaseAccount(models.Model):
    class Meta:
        abstract = True
