# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('colab_wikilegis', '0005_auto_20170323_2025'),
    ]

    operations = [
        migrations.AddField(
            model_name='wikilegisbill',
            name='theme',
            field=models.ForeignKey(to='colab_wikilegis.WikilegisBillTheme', null=True),
            preserve_default=True,
        ),
    ]
