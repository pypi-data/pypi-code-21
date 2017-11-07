# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pages.utils.image
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_insert_default_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='picture_mobile',
            field=imagekit.models.fields.ProcessedImageField(null=True, upload_to=pages.utils.image.upload_picture_to),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='picture_pc',
            field=imagekit.models.fields.ProcessedImageField(default=1, upload_to=pages.utils.image.upload_picture_to),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='page',
            name='picture_share',
            field=imagekit.models.fields.ProcessedImageField(null=True, upload_to=pages.utils.image.upload_picture_to),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='picture_tablet',
            field=imagekit.models.fields.ProcessedImageField(null=True, upload_to=pages.utils.image.upload_picture_to),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='type',
            field=models.SmallIntegerField(default=1, choices=[(1, b'General')]),
            preserve_default=True,
        ),
    ]
