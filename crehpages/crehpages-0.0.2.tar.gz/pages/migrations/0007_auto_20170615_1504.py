# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0006_seotag'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageTimer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('is_active', models.BooleanField(default=False)),
                ('identifier', models.URLField()),
                ('title', models.CharField(max_length=250)),
                ('expire_date', models.DateTimeField()),
            ],
            options={
                'db_table': 'pages_timer',
            },
            bases=(models.Model,),
        ),
        migrations.RenameModel(
            old_name='SEOTag',
            new_name='PageSEO',
        ),
    ]
