# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0005_auto_20170608_1255'),
    ]

    operations = [
        migrations.CreateModel(
            name='SEOTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('is_active', models.BooleanField(default=False)),
                ('url', models.URLField()),
                ('title', models.CharField(max_length=250)),
                ('description', models.CharField(max_length=250)),
                ('keywords', models.CharField(max_length=250)),
                ('page_type', models.CharField(max_length=250)),
                ('share_image', models.ImageField(upload_to=b'')),
                ('canonical_url', models.URLField()),
            ],
            options={
                'db_table': 'pages_seo',
            },
            bases=(models.Model,),
        ),
    ]
