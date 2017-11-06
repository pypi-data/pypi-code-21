# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.SlugField(verbose_name='name', unique=True, editable=False)),
                ('title', models.CharField(verbose_name='title', unique=True, max_length=100)),
                ('content', models.TextField(verbose_name='content')),
            ],
            options={
                'verbose_name': 'page',
                'verbose_name_plural': 'pages',
            },
        ),
    ]
