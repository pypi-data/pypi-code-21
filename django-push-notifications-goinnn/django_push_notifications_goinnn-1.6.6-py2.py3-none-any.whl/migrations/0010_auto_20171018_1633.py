# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('push_notifications', '0009_auto_20171018_1623'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='apnsdevice',
            name='company',
        ),
        migrations.RemoveField(
            model_name='firefoxdevice',
            name='company',
        ),
        migrations.RemoveField(
            model_name='gcmdevice',
            name='company',
        ),
        migrations.RemoveField(
            model_name='webpushdevice',
            name='company',
        ),
        migrations.RemoveField(
            model_name='wnsdevice',
            name='company',
        ),
    ]
