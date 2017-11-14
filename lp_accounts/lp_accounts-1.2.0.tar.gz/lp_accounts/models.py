from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


# Create your models here.
class User(AbstractUser):
    TYPE_DEFAULT = 1
    TYPE_GOOGLE = 2
    TYPE_FACEBOOK = 3
    TYPE_GITHUB = 4
    TYPE_LINKEDIN = 5
    TYPES = (
        (TYPE_DEFAULT, 'Default'),
        (TYPE_GOOGLE, 'Google'),
        (TYPE_FACEBOOK, 'Facebook'),
        (TYPE_GITHUB, 'Github'),
        (TYPE_LINKEDIN, 'LinkedIn'),
    )

    type = models.IntegerField(choices=TYPES, default=TYPE_DEFAULT)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    account_id = models.PositiveIntegerField(null=True)
    account = GenericForeignKey('content_type', 'account_id')

    def __str__(self):
        return self.username


class BaseAccount(models.Model):
    class Meta:
        abstract = True
