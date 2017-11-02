# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def copy_date(apps, schema_editor):
    Document = apps.get_model('glitter_documents', 'Document')
    for document in Document.objects.all():
        document.publish_at = document.created_at
        document.save()

class Migration(migrations.Migration):

    dependencies = [
        ('glitter_documents', '0004_add_field_publish_at'),
    ]

    operations = [
        migrations.RunPython(copy_date),
    ]
