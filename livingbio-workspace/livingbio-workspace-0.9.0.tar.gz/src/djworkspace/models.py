# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from picklefield.fields import PickledObjectField

# Create your models here.


class Cache(models.Model):
    type = models.CharField(max_length=40)
    key = models.CharField(max_length=40)

    results = PickledObjectField()

    class Meta:
        unique_together = (('type', 'key'), )
