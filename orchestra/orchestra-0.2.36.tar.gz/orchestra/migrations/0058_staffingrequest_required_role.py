# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-02 09:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orchestra', '0057_auto_20160429_1127'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffingrequest',
            name='required_role',
            field=models.IntegerField(
                choices=[(0, 'Entry-level'), (1, 'Reviewer')], default=0),
        ),
    ]
