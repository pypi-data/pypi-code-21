from django.db import models

# Create your models here.
from slxauth.models import AbstractSolarluxUser


class MyUser(AbstractSolarluxUser):

    example_field = models.CharField(max_length=250)

