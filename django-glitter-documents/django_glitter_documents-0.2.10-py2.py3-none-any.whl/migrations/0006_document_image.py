# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import glitter.assets.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('glitter_assets', '0002_image_category_field_optional'),
        ('glitter_documents', '0005_copy_date_created_to_publish'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='image',
            field=glitter.assets.fields.AssetForeignKey(help_text='Preview document image', null=True, on_delete=django.db.models.deletion.PROTECT, blank=True, to='glitter_assets.Image'),
        ),
    ]
