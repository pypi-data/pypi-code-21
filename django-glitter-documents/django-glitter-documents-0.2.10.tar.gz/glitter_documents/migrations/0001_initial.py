# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('glitter', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('title', models.CharField(max_length=100, db_index=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
            ],
            options={
                'ordering': ('title',),
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('published', models.BooleanField(default=True, db_index=True)),
                ('title', models.CharField(max_length=100, db_index=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('document', models.FileField(max_length=200, upload_to='documents/document/%Y/%m')),
                ('valid_image', models.BooleanField(editable=False, default=False)),
                ('author', models.CharField(max_length=32, blank=True)),
                ('file_size', models.PositiveIntegerField(editable=False, default=0)),
                ('summary', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('category', models.ForeignKey(to='glitter_documents.Category')),
                ('current_version', models.ForeignKey(editable=False, blank=True, to='glitter.Version', null=True)),
            ],
            options={
                'get_latest_by': 'created_at',
                'abstract': False,
                'default_permissions': ('add', 'change', 'delete', 'edit', 'publish'),
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Format',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('title', models.CharField(max_length=100, db_index=True)),
            ],
            options={
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='LatestDocumentsBlock',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('category', models.ForeignKey(blank=True, to='glitter_documents.Category', null=True)),
                ('content_block', models.ForeignKey(editable=False, null=True, to='glitter.ContentBlock')),
            ],
            options={
                'verbose_name': 'latest documents',
            },
        ),
        migrations.AddField(
            model_name='document',
            name='document_format',
            field=models.ForeignKey(to='glitter_documents.Format'),
        ),
    ]
