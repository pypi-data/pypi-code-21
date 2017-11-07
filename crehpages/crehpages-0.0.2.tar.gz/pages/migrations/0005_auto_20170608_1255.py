# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_product'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('seo_title', models.CharField(max_length=100)),
                ('seo_sub_title', models.CharField(max_length=100)),
                ('seo_desc', models.CharField(max_length=100)),
                ('seo_keywords', models.CharField(max_length=100)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('is_active', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=230)),
                ('page', models.ForeignKey(to='pages.Page')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='page',
            name='slug',
            field=models.SlugField(max_length=230),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='title',
            field=models.CharField(max_length=200),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='product',
            name='reference_id',
            field=models.CharField(unique=True, max_length=20),
            preserve_default=True,
        ),
    ]
