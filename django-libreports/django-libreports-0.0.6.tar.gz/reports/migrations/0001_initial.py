# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import reports.models
import django.utils.timezone
import jsonfield.fields
import django.contrib.postgres.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('django_celery_beat', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        migrations.swappable_dependency(settings.ORGANIZATION_MODEL)
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('report', models.CharField(max_length=64)),
                ('typ', models.CharField(max_length=32, choices=[(b'docx', b'Word Doc')])),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('emails', django.contrib.postgres.fields.ArrayField(null=True, base_field=models.EmailField(max_length=255), size=None)),
                ('name', models.CharField(max_length=64, blank=True)),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField()),
                ('config', jsonfield.fields.JSONField(default={}, blank=True)),
                ('document', models.FileField(null=True, upload_to=reports.models.report_upload_to, blank=True)),
                ('created_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('organization', models.ForeignKey(to=settings.ORGANIZATION_MODEL)),
            ],
            options={
                'verbose_name': 'Report',
                'verbose_name_plural': 'Reports',
            },
        ),
        migrations.CreateModel(
            name='ReportSchedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('report', models.CharField(max_length=64)),
                ('typ', models.CharField(max_length=32, choices=[(b'docx', b'Word Doc')])),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('emails', django.contrib.postgres.fields.ArrayField(null=True, base_field=models.EmailField(max_length=255), size=None)),
                ('schedule', jsonfield.fields.JSONField(default={}, blank=True)),
                ('period', models.CharField(default=b'weekly', max_length=32, choices=[(b'daily', b'Daily'), (b'weekly', b'Weekly'), (b'monthly', b'Monthly'), (b'quarterly', b'Quarterly'), (b'yearly', b'Yearly')])),
                ('created_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('organization', models.ForeignKey(to=settings.ORGANIZATION_MODEL)),
                ('periodic_task', models.ForeignKey(blank=True, to='django_celery_beat.PeriodicTask', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
