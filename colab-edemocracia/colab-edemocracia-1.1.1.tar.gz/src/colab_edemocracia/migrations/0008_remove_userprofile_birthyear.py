# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('colab_edemocracia', '0007_auto_20171006_1902'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='birthyear',
        ),
    ]
