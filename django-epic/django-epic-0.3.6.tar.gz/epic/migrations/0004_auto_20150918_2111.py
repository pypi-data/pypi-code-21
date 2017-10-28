# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal
import epic.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('epic', '0003_auto_20150915_1436'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasheet',
            name='md5sum',
            field=models.CharField(null=True, max_length=36),
        ),
    ]
