# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commenting', '0002_auto_20151105_1214'),
    ]

    operations = [
        migrations.CreateModel(
            name='CannedResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('response_header', models.CharField(max_length=500)),
                ('response', models.TextField(max_length=3000)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['response_header', 'response'],
                'verbose_name_plural': 'Canned responses',
            },
        ),
    ]
