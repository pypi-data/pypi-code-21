# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('colab_audiencias', '0004_auto_20170403_2118'),
    ]

    operations = [
        migrations.AddField(
            model_name='audienciasroom',
            name='is_joint',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='audienciasroom',
            name='reunion_type',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='audienciasroom',
            name='title_reunion',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
    ]
