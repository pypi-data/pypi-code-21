# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('push_notifications', '0007_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='firefoxdevice',
            name='application_id',
            field=models.CharField(help_text='Opaque application identity, should be filled in for multiple key/certificate access', max_length=64, null=True, verbose_name='Application ID', blank=True),
        ),
        migrations.AddField(
            model_name='webpushdevice',
            name='company',
            field=models.CharField(default='', max_length=255, null=True, verbose_name='Company', blank=True),
        ),
    ]
