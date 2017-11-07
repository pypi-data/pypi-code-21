# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0014_auto_20170630_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='page_size',
            field=models.SmallIntegerField(default=9),
            preserve_default=True,
        ),
    ]
