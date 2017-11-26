# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_googlecalendar', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='googlecalendar',
            name='api_key',
            field=models.CharField(max_length=255, default=1, verbose_name='Google Calendar API Key'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='googlecalendar',
            name='calendar_id',
            field=models.CharField(max_length=255, default=1, verbose_name='Google Calendar ID'),
            preserve_default=False,
        ),
    ]
