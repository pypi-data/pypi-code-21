from django.db import models
from core_flavor import models as core_models


class TimeStampedUUID(core_models.TimeStampedUUIDModel):
    name = models.CharField(max_length=20)


class SoftDeletable(core_models.SoftDeletableModel):
    name = models.CharField(max_length=20)
