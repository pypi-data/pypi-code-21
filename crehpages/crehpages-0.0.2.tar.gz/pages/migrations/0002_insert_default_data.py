# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def insert_default_data(apps, schema_editor):
    SliderContentType = apps.get_model('pages', 'SliderContentType')
    data = [
        "Text",
        "Description",
        "Button"
    ]

    for slider_type in data:
        slider_content_type = SliderContentType()
        slider_content_type.name = slider_type
        slider_content_type.save()


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(insert_default_data)
    ]
