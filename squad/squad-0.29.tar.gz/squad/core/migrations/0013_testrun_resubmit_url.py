# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-30 18:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_build_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='testrun',
            name='resubmit_url',
            field=models.CharField(max_length=2048, null=True),
        ),
    ]
