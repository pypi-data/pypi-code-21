# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0007_auto_20170615_1504'),
    ]

    operations = [
        migrations.RenameField(
            model_name='page',
            old_name='picture_mobile',
            new_name='banner_mobile',
        ),
        migrations.RenameField(
            model_name='page',
            old_name='picture_pc',
            new_name='banner_pc',
        ),
        migrations.RenameField(
            model_name='page',
            old_name='picture_share',
            new_name='banner_share',
        ),
        migrations.RenameField(
            model_name='page',
            old_name='picture_tablet',
            new_name='banner_tablet',
        ),
        migrations.RenameField(
            model_name='page',
            old_name='type',
            new_name='page_type',
        ),
        migrations.AddField(
            model_name='page',
            name='subtitle',
            field=models.CharField(max_length=200, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='slug',
            field=models.SlugField(max_length=230, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pageseo',
            name='url',
            field=models.SlugField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pagetimer',
            name='identifier',
            field=models.SlugField(),
            preserve_default=True,
        ),
    ]
