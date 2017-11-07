# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0009_auto_20170616_0141'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='timer_id',
            field=models.SlugField(max_length=100, null=True),
            preserve_default=True,
        ),
    ]
