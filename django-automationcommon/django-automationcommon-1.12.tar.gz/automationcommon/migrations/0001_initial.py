# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Audit',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('when', models.DateTimeField(auto_now=True)),
                ('model', models.CharField(max_length=64)),
                ('model_pk', models.IntegerField()),
                ('field', models.CharField(max_length=64)),
                ('old', models.CharField(blank=True, max_length=255, null=True)),
                ('new', models.CharField(blank=True, max_length=255, null=True)),
                ('who', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
