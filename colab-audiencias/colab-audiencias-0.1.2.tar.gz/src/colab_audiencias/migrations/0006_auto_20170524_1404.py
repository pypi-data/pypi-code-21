# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('colab_audiencias', '0005_auto_20170420_2029'),
    ]

    operations = [
        migrations.AddField(
            model_name='audienciasroom',
            name='date',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='audienciasroom',
            name='reunion_object',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='audienciasroom',
            name='reunion_theme',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
