# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('colab_edemocracia', '0004_userprofile_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='birthyear',
            field=models.IntegerField(max_length=4, null=True, blank=True),
            preserve_default=True,
        ),
    ]
