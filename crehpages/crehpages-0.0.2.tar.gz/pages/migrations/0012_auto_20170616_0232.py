# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pages.utils.image
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0011_auto_20170616_0214'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pageseo',
            old_name='url',
            new_name='slug',
        ),
        migrations.RemoveField(
            model_name='page',
            name='banner_share',
        ),
        migrations.RemoveField(
            model_name='pageseo',
            name='share_image',
        ),
        migrations.AddField(
            model_name='pageseo',
            name='banner_share',
            field=imagekit.models.fields.ProcessedImageField(null=True, upload_to=pages.utils.image.upload_picture_to, blank=True),
            preserve_default=True,
        ),
    ]
