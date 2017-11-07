# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0010_page_timer_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='social_buttons',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='subtitle_custom_color',
            field=models.CharField(max_length=7, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='title_custom_color',
            field=models.CharField(max_length=7, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='timer_id',
            field=models.SlugField(max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
    ]
