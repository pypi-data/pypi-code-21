# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-10-15 17:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opensubmit', '0022_assignment_max_authors'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='max_authors',
        ),
    ]
