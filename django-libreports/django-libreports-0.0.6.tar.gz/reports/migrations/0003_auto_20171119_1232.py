# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import reports.models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0002_auto_20171117_1004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='document',
            field=models.FileField(max_length=1024, null=True, upload_to=reports.models.report_upload_to, blank=True),
        ),
    ]
