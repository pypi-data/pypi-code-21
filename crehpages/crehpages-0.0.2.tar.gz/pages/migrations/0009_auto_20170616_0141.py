# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pages.utils.image
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0008_auto_20170616_0136'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='seo_desc',
        ),
        migrations.RemoveField(
            model_name='page',
            name='seo_keywords',
        ),
        migrations.RemoveField(
            model_name='page',
            name='seo_sub_title',
        ),
        migrations.RemoveField(
            model_name='page',
            name='seo_title',
        ),
        migrations.AlterField(
            model_name='page',
            name='banner_mobile',
            field=imagekit.models.fields.ProcessedImageField(null=True, upload_to=pages.utils.image.upload_picture_to, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='banner_pc',
            field=imagekit.models.fields.ProcessedImageField(upload_to=pages.utils.image.upload_picture_to, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='banner_share',
            field=imagekit.models.fields.ProcessedImageField(null=True, upload_to=pages.utils.image.upload_picture_to, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='banner_tablet',
            field=imagekit.models.fields.ProcessedImageField(null=True, upload_to=pages.utils.image.upload_picture_to, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='page_type',
            field=models.SmallIntegerField(default=1, blank=True, choices=[(1, b'General')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='subtitle',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
    ]
