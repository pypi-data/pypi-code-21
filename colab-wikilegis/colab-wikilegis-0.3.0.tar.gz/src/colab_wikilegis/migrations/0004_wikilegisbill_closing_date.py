# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('colab_wikilegis', '0003_auto_20160909_1804'),
    ]

    operations = [
        migrations.AddField(
            model_name='wikilegisbill',
            name='closing_date',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
