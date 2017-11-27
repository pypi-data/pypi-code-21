from __future__ import absolute_import, unicode_literals

from django.db import models


class Timestamps(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
