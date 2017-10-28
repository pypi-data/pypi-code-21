# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epic', '0002_auto_20150128_2344'),
    ]

    operations = [
        migrations.CreateModel(
            name='Datasheet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128)),
                ('ds_file', models.FileField(upload_to=b'datasheets')),
                ('notes', models.CharField(help_text=b'For misc. information that may be useful along with the datasheet, such as website retrieved from.', max_length=1024, blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='part',
            name='datasheet',
            field=models.ForeignKey(blank=True, to='epic.Datasheet', null=True),
        ),
    ]
