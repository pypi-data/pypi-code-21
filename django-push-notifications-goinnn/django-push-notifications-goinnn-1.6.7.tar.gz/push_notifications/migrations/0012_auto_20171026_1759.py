# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('push_notifications', '0011_auto_20171018_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webpushdevice',
            name='auth',
            field=models.CharField(max_length=24, verbose_name='User auth secret'),
        ),
        migrations.AlterField(
            model_name='webpushdevice',
            name='p256dh',
            field=models.CharField(max_length=88, verbose_name='User public encryption key'),
        ),
    ]
