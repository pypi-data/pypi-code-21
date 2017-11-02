# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('glitter_documents', '0003_category_parent_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='document',
            options={'default_permissions': ('add', 'change', 'delete', 'edit', 'publish'), 'get_latest_by': 'publish_at', 'ordering': ('-publish_at',)},
        ),
        migrations.AddField(
            model_name='document',
            name='publish_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
    ]
