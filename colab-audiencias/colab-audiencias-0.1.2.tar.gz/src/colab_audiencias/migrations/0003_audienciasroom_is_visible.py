# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('colab_audiencias', '0002_auto_20170323_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='audienciasroom',
            name='is_visible',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
