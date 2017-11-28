# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('colab_wikilegis', '0006_wikilegisbill_theme'),
    ]

    operations = [
        migrations.CreateModel(
            name='WikilegisSegment',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('number', models.PositiveIntegerField(default=0, null=True, blank=True)),
                ('content', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('bill', models.ForeignKey(related_name='segments', to='colab_wikilegis.WikilegisBill')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WikilegisSegmentType',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=999)),
                ('presentation_name', models.CharField(max_length=999)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='wikilegissegment',
            name='segment_type',
            field=models.ForeignKey(to='colab_wikilegis.WikilegisSegmentType'),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='wikilegisbill',
            name='reporting_member',
        ),
    ]
