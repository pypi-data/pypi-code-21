# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone


class SEOMixin(models.Model):

    seo_title = models.CharField(
        max_length=100,
    )

    seo_sub_title = models.CharField(
        max_length=100,
    )

    seo_desc = models.CharField(
        max_length=100,
    )

    seo_keywords = models.CharField(
        max_length=100,
    )

    class Meta:
        abstract = True


class AuditableMixin(models.Model):

    created = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )

    modified = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )

    class Meta:
        abstract = True


class ActivatedMixin(models.Model):
    """
    """
    is_active = models.BooleanField(default=False)

    class Meta:
        abstract = True


class ActivatedQuerySet(models.QuerySet):

    def not_activated(self):
        return self.filter(is_active=False)

    def activated(self):
        return self.filter(is_active=True)
