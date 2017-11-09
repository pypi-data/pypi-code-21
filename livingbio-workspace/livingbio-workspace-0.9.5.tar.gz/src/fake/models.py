# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Fake(models.Model):
    field = models.FileField()
