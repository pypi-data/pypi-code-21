# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0012_auto_20170616_0232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='reference_id',
            field=models.CharField(max_length=40),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='product',
            unique_together=set([('page', 'reference_id')]),
        ),
    ]
