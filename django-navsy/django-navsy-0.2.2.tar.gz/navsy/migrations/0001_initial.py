# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import autoslug.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parents_pks', models.CharField(blank=True, default='', editable=False, max_length=500)),
                ('parents_count', models.PositiveSmallIntegerField(default=0, editable=False)),
                ('children_pks', models.CharField(blank=True, default='', editable=False, max_length=500)),
                ('children_count', models.PositiveSmallIntegerField(default=0, editable=False)),
                ('siblings_pks', models.CharField(blank=True, default='', editable=False, max_length=500)),
                ('siblings_count', models.PositiveSmallIntegerField(default=0, editable=False)),
                ('priority', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(9999)])),
                ('priorities', models.CharField(blank=True, default='', editable=False, max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('slug', autoslug.fields.AutoSlugField(always_update=True, blank=True, editable=False, null=True, populate_from='name', unique=True)),
                ('home', models.BooleanField(default=False)),
                ('menu', models.BooleanField(default=True)),
                ('published', models.BooleanField(default=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='navsy.Page')),
            ],
            options={
                'ordering': ['-priorities'],
                'verbose_name': 'Page',
                'verbose_name_plural': 'Pages',
            },
        ),
        migrations.CreateModel(
            name='Pattern',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('regex', models.CharField(blank=True, default='', max_length=255, unique=True)),
                ('regex_display', models.CharField(blank=True, default='', editable=False, max_length=255)),
                ('regex_format', models.CharField(blank=True, default='', editable=False, max_length=255)),
            ],
            options={
                'ordering': ['regex'],
                'verbose_name': 'Pattern',
                'verbose_name_plural': 'Patterns',
            },
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('view_name', models.CharField(blank=True, db_index=True, help_text='(unique name used for reverse URL)', max_length=100, null=True, unique=True)),
                ('view_function_path', models.CharField(blank=True, help_text='(ex. app.views.view_func)', max_length=100)),
                ('view_template_path', models.CharField(blank=True, help_text='(ex. app/template.html)', max_length=100)),
                ('redirect_to_first_child_page', models.BooleanField(default=False)),
                ('redirect_to_path', models.CharField(blank=True, max_length=200)),
                ('redirect_to_url', models.URLField(blank=True)),
                ('priority', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(9999)])),
                ('page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='routes', to='navsy.Page')),
                ('pattern', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='navsy.Pattern')),
                ('redirect_to_page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='navsy.Page')),
            ],
            options={
                'ordering': ['page', '-priority'],
                'verbose_name': 'Route',
                'verbose_name_plural': 'Routes',
            },
        ),
        migrations.AlterUniqueTogether(
            name='route',
            unique_together=set([('page', 'pattern')]),
        ),
    ]
