# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('push_notifications', '0010_auto_20171018_1633'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='firefoxdevice',
            name='user',
        ),
        migrations.DeleteModel(
            name='FirefoxDevice',
        ),
    ]
