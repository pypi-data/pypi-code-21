# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-28 14:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codenerix_products', '0004_auto_20170307_1045'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='name',
        ),
    ]
