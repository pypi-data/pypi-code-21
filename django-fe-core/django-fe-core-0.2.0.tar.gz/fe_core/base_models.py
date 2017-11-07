# -*- coding:utf-8 -*-
import uuid
from django.db import models


class UUIDModel(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_uuid(self):
        return str(self.uuid)[0:8]

    get_uuid.short_description = 'UUID'

    class Meta:
        abstract = True
