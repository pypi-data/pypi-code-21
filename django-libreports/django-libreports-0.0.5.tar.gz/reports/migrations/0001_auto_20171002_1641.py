# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='emails',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.EmailField(max_length=255), blank=True),
        ),
        migrations.AlterField(
            model_name='reportschedule',
            name='emails',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.EmailField(max_length=255), blank=True),
        )
    ]
