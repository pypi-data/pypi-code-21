# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_auto_20171002_1641'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportschedule',
            name='config',
            field=jsonfield.fields.JSONField(default={}, blank=True),
        ),
    ]
