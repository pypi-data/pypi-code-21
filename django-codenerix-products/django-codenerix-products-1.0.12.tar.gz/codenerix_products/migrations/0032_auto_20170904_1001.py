# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-04 08:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codenerix_products', '0031_auto_20170901_1256'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='typerecargoequivalencia',
            name='type_tax',
        ),
        migrations.DeleteModel(
            name='TypeRecargoEquivalencia',
        ),
    ]
